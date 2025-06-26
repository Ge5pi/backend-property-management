import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from communication.models import AnnouncementAttachment
from communication.views import AnnouncementAttachmentByAnnouncementListAPIView, AnnouncementAttachmentViewSet


@pytest.mark.django_db
def test_announcement_attachment_list(
    api_rf, user_with_permissions, announcement_attachment_factory, announcement_factory
):
    """
    Testing :py:meth:`communication.views.AnnouncementAttachmentByAnnouncementListAPIView` method.
    """
    user = user_with_permissions([("communication", "announcementattachment")])
    announcement = announcement_factory(id=200, subscription=user.associated_subscription)
    instance_1 = announcement_attachment_factory(announcement=announcement, subscription=user.associated_subscription)
    instance_2 = announcement_attachment_factory(announcement=announcement, subscription=user.associated_subscription)
    instance_3 = announcement_attachment_factory(announcement=announcement, subscription=user.associated_subscription)
    announcement_attachment_factory()
    index_result = [2, 1, 0]

    announcement_attachments = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(3):
        url = reverse(
            "communication:announcement-attachment-list",
            kwargs={"announcement_id": 200},
        )
        request = api_rf.get(url, {}, format="json")
        request.user = user
        view = AnnouncementAttachmentByAnnouncementListAPIView.as_view()
        response = view(request, announcement_id=announcement.id)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [announcement_attachments[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "announcement": ["This field is required."],
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
                "announcement": 100,
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
def test_announcement_attachment_create(
    api_rf,
    property_factory,
    tag_factory,
    announcement_factory,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`communication.views.AnnouncementAttachmentViewSet.create` method.
    """

    user = user_with_permissions([("communication", "announcementattachment")])
    announcement_factory(id=100)
    property_factory(id=100)
    tag_factory(id=100)
    tag_factory(id=200)

    with assertNumQueries(num_queries):
        url = reverse("communication:announcement-attachment-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = AnnouncementAttachmentViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert AnnouncementAttachment.objects.count() == obj_count


@pytest.mark.django_db
def test_announcement_attachment_retrieve(api_rf, announcement_attachment_factory, user_with_permissions):
    """
    Testing :py:meth:`communication.views.AnnouncementAttachmentViewSet.retrieve` method.
    """

    user = user_with_permissions([("communication", "announcementattachment")])
    announcement_attachment = announcement_attachment_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse(
            "communication:announcement-attachment-detail",
            kwargs={"pk": announcement_attachment.id},
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = AnnouncementAttachmentViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=announcement_attachment.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "name",
        "created_by",
        "file",
        "announcement",
        "file_type",
        "updated_at",
    }


@pytest.mark.django_db
def test_announcement_attachment_update(
    api_rf, announcement_attachment_factory, user_with_permissions, announcement_factory
):
    """
    Testing :py:meth:`communication.views.AnnouncementAttachmentViewSet.partial_update` method.
    """

    user = user_with_permissions([("communication", "announcementattachment")])
    announcement = announcement_factory(subscription=user.associated_subscription)
    announcement_attachment = announcement_attachment_factory(subscription=user.associated_subscription)
    data = {
        "announcement": announcement.id,
        "file": "Agreement.pdf",
        "name": "Agreement",
        "file_type": "pdf",
    }

    with assertNumQueries(5):
        url = reverse(
            "communication:announcement-attachment-detail",
            kwargs={"pk": announcement_attachment.id},
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = AnnouncementAttachmentViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=announcement_attachment.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_announcement_attachment_delete(api_rf, announcement_attachment_factory, user_with_permissions):
    """
    Testing :py:meth:`communication.views.AnnouncementAttachmentViewSet.delete` method.
    """

    user = user_with_permissions([("communication", "announcementattachment")])
    announcement_attachment = announcement_attachment_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse(
            "communication:announcement-attachment-detail",
            kwargs={"pk": announcement_attachment.id},
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = AnnouncementAttachmentViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=announcement_attachment.id)

    assert response.status_code == 204

    assert AnnouncementAttachment.objects.count() == 0
