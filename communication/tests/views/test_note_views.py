import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from communication.models import Note
from communication.views import NoteViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 7),
        ({"search": "heavy great"}, [0], 5),
        ({"search": "seek better"}, [1], 5),
        ({"ordering": "title"}, [0, 2, 1], 7),
        ({"ordering": "-title"}, [1, 2, 0], 7),
        ({"ordering": "associated_property"}, [2, 1, 0], 7),
        ({"ordering": "-associated_property"}, [0, 1, 2], 7),
        ({"ordering": "pk"}, [0, 1, 2], 7),
        ({"ordering": "-pk"}, [2, 1, 0], 7),
    ),
)
@pytest.mark.django_db
def test_note_list(
    api_rf, user_with_permissions, note_factory, property_factory, query_params, index_result, num_queries
):
    """
    Testing :py:meth:`communication.views.NoteViewSet.list` method.
    """
    user = user_with_permissions([("communication", "note")])

    prop_1 = property_factory(id=300)
    prop_2 = property_factory(id=200)
    prop_3 = property_factory(id=100)

    instance_1 = note_factory(
        title="Fly heavy great work.", associated_property=prop_1, subscription=user.associated_subscription
    )
    instance_2 = note_factory(
        title="Toward.",
        description="Edge husband seek better. Enter yeah huge.",
        associated_property=prop_2,
        subscription=user.associated_subscription,
    )
    instance_3 = note_factory(title="Himself.", associated_property=prop_3, subscription=user.associated_subscription)
    note_factory()

    notes = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("communication:note-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = NoteViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [notes[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "title": ["This field is required."],
                "description": ["This field is required."],
                "associated_property": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "title": "Note title",
                "description": "Note description",
                "associated_property": 100,
                "tags": [100],
            },
            None,
            201,
            9,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_note_create(
    api_rf,
    property_factory,
    tag_factory,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`communication.views.NoteViewSet.create` method.
    """

    user = user_with_permissions([("communication", "note")])
    property_factory(id=100)
    tag_factory(id=100)
    tag_factory(id=200)

    with assertNumQueries(num_queries):
        url = reverse("communication:note-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = NoteViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert Note.objects.count() == obj_count


@pytest.mark.django_db
def test_note_retrieve(api_rf, note_factory, user_with_permissions):
    """
    Testing :py:meth:`communication.views.NoteViewSet.retrieve` method.
    """

    user = user_with_permissions([("communication", "note")])
    note = note_factory(subscription=user.associated_subscription)

    with assertNumQueries(5):
        url = reverse("communication:note-detail", kwargs={"pk": note.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = NoteViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=note.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "title",
        "description",
        "associated_property",
        "tags",
        "created_by_full_name",
        "modified_by_full_name",
        "tag_names",
        "created_at",
        "updated_at",
        "associated_property_name",
        "associated_property_type_name",
    }


@pytest.mark.django_db
def test_note_update(api_rf, note_factory, user_with_permissions, property_factory, tag_factory):
    """
    Testing :py:meth:`communication.views.NoteViewSet.partial_update` method.
    """

    user = user_with_permissions([("communication", "note")])
    note = note_factory(subscription=user.associated_subscription)
    prop = property_factory()
    tag = tag_factory()
    data = {
        "title": "Fly heavy great work",
        "description": "Edge husband seek better. Enter yeah huge.",
        "associated_property": prop.id,
        "tags": [tag.id],
    }

    with assertNumQueries(11):
        url = reverse("communication:note-detail", kwargs={"pk": note.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = NoteViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=note.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_note_delete(api_rf, note_factory, user_with_permissions):
    """
    Testing :py:meth:`communication.views.NoteViewSet.delete` method.
    """

    user = user_with_permissions([("communication", "note")])
    note = note_factory(subscription=user.associated_subscription)

    with assertNumQueries(7):
        url = reverse("communication:note-detail", kwargs={"pk": note.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = NoteViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=note.id)

    assert response.status_code == 204

    assert Note.objects.count() == 0
