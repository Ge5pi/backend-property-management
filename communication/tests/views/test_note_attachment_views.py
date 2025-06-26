import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from communication.models import NoteAttachment
from communication.views import NoteAttachmentByNoteListAPIView, NoteAttachmentViewSet


@pytest.mark.django_db
def test_note_attachment_list(api_rf, user_with_permissions, note_attachment_factory, note_factory):
    """
    Testing :py:meth:`communication.views.NoteAttachmentByNoteListAPIView` method.
    """
    user = user_with_permissions([("communication", "noteattachment")])
    note = note_factory(id=200)
    instance_1 = note_attachment_factory(note=note, subscription=user.associated_subscription)
    instance_2 = note_attachment_factory(note=note, subscription=user.associated_subscription)
    instance_3 = note_attachment_factory(note=note, subscription=user.associated_subscription)
    note_attachment_factory()
    index_result = [2, 1, 0]

    note_attachments = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(3):
        url = reverse("communication:note-attachment-list", kwargs={"note_id": 200})
        request = api_rf.get(url, {}, format="json")
        request.user = user
        view = NoteAttachmentByNoteListAPIView.as_view()
        response = view(request, note_id=note.id)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [note_attachments[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "note": ["This field is required."],
                "file": ["This field is required."],
                "name": ["This field is required."],
                "file_type": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "note": 100,
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            None,
            201,
            8,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_note_attachment_create(
    api_rf,
    property_factory,
    tag_factory,
    note_factory,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`communication.views.NoteAttachmentViewSet.create` method.
    """

    user = user_with_permissions([("communication", "noteattachment")])
    note_factory(id=100)
    property_factory(id=100)
    tag_factory(id=100)
    tag_factory(id=200)

    with assertNumQueries(num_queries):
        url = reverse("communication:note-attachment-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = NoteAttachmentViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert NoteAttachment.objects.count() == obj_count


@pytest.mark.django_db
def test_note_attachment_retrieve(api_rf, note_attachment_factory, note_factory, user_with_permissions):
    """
    Testing :py:meth:`communication.views.NoteAttachmentViewSet.retrieve` method.
    """

    user = user_with_permissions([("communication", "noteattachment")])
    note_attachment = note_attachment_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse(
            "communication:note-attachment-detail",
            kwargs={"pk": note_attachment.id},
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = NoteAttachmentViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=note_attachment.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "name",
        "created_by",
        "file",
        "note",
        "file_type",
        "updated_at",
    }


@pytest.mark.django_db
def test_note_attachment_update(api_rf, note_attachment_factory, user_with_permissions, note_factory):
    """
    Testing :py:meth:`communication.views.NoteAttachmentViewSet.partial_update` method.
    """

    user = user_with_permissions([("communication", "noteattachment")])
    note = note_factory()
    note_attachment = note_attachment_factory(subscription=user.associated_subscription)
    data = {
        "note": note.id,
        "file": "Agreement.pdf",
        "name": "Agreement",
        "file_type": "pdf",
    }

    with assertNumQueries(5):
        url = reverse(
            "communication:note-attachment-detail",
            kwargs={"pk": note_attachment.id},
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = NoteAttachmentViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=note_attachment.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_note_attachment_delete(api_rf, note_attachment_factory, user_with_permissions, note_factory):
    """
    Testing :py:meth:`communication.views.NoteAttachmentViewSet.delete` method.
    """

    user = user_with_permissions([("communication", "noteattachment")])
    note_attachment = note_attachment_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse(
            "communication:note-attachment-detail",
            kwargs={"pk": note_attachment.id},
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = NoteAttachmentViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=note_attachment.id)

    assert response.status_code == 204

    assert NoteAttachment.objects.count() == 0
