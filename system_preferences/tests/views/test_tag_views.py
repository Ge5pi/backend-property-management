import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from system_preferences.models import Tag
from system_preferences.views import TagViewSet


@pytest.mark.parametrize(
    "query_params, index_result",
    (
        ({}, [2, 1, 0]),
        ({"ordering": "created_at"}, [0, 1, 2]),
        ({"ordering": "-created_at"}, [2, 1, 0]),
        ({"search": "uild"}, [0]),
        ({"search": "part"}, [1]),
        ({"search": "hop"}, [2]),
    ),
)
@pytest.mark.django_db
def test_tag_list(api_rf, user_with_permissions, tag_factory, query_params, index_result):
    """
    Testing :py:meth:`system_preferences.views.TagViewSet.list` method.
    """
    user = user_with_permissions([("system_preferences", "tag")])

    instance_1 = tag_factory(name="Building", subscription=user.associated_subscription)
    instance_2 = tag_factory(name="Apartment", subscription=user.associated_subscription)
    instance_3 = tag_factory(name="Shop", subscription=user.associated_subscription)
    tag_factory()

    tags = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(3):
        url = reverse("system_preferences:tag-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = TagViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [tags[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        ({}, {"name": ["This field is required."]}, 400, 2, 0),
        ({"name": ""}, {"name": ["This field may not be blank."]}, 400, 2, 0),
        ({"name": "Building"}, None, 201, 4, 1),
    ),
)
@pytest.mark.django_db
def test_tag_create(api_rf, user_with_permissions, data, expected_response, status_code, num_queries, obj_count):
    """
    Testing :py:meth:`system_preferences.views.TagViewSet.create` method.
    """
    user = user_with_permissions([("system_preferences", "tag")])

    with assertNumQueries(num_queries):
        url = reverse("system_preferences:tag-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = TagViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert Tag.objects.count() == obj_count


@pytest.mark.django_db
def test_tag_retrieve(api_rf, tag_factory, user_with_permissions):
    """
    Testing :py:meth:`system_preferences.views.TagViewSet.retrieve` method.
    """

    user = user_with_permissions([("system_preferences", "tag")])
    tag = tag_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse("system_preferences:tag-detail", kwargs={"pk": tag.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = TagViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=tag.id)

    assert response.status_code == 200

    assert response.data.keys() == {"id", "name", "items_count"}


@pytest.mark.parametrize(
    "data",
    ({"name": "Building"}, {"name": "Society"}),
)
@pytest.mark.django_db
def test_tag_update(api_rf, tag_factory, user_with_permissions, data):
    """
    Testing :py:meth:`system_preferences.views.TagViewSet.partial_update` method.
    """

    user = user_with_permissions([("system_preferences", "tag")])
    tag = tag_factory(subscription=user.associated_subscription)

    with assertNumQueries(5):
        url = reverse("system_preferences:tag-detail", kwargs={"pk": tag.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = TagViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=tag.id)

    assert response.status_code == 200
    assert response.data["name"] == data["name"]


@pytest.mark.django_db
def test_tag_delete(api_rf, tag_factory, user_with_permissions):
    """
    Testing :py:meth:`system_preferences.views.TagViewSet.delete` method.
    """

    user = user_with_permissions([("system_preferences", "tag")])
    tag = tag_factory(subscription=user.associated_subscription)

    with assertNumQueries(7):
        url = reverse("system_preferences:tag-detail", kwargs={"pk": tag.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = TagViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=tag.id)

    assert response.status_code == 204

    assert Tag.objects.count() == 0
