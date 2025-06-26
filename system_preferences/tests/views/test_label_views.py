import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from system_preferences.models import Label
from system_preferences.views import LabelViewSet


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
def test_label_list(api_rf, user_with_permissions, label_factory, query_params, index_result):
    """
    Testing :py:meth:`system_preferences.views.LabelViewSet.list` method.
    """
    user = user_with_permissions([("system_preferences", "label")])

    instance_1 = label_factory(name="Building", subscription=user.associated_subscription)
    instance_2 = label_factory(name="Apartment", subscription=user.associated_subscription)
    instance_3 = label_factory(name="Shop", subscription=user.associated_subscription)
    label_factory()

    labels = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(3):
        url = reverse("system_preferences:label-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = LabelViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [labels[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        ({}, {"name": ["This field is required."]}, 400, 2, 0),
        ({"name": ""}, {"name": ["This field may not be blank."]}, 400, 2, 0),
        ({"name": "Building"}, None, 201, 4, 1),
    ),
)
@pytest.mark.django_db
def test_label_create(api_rf, user_with_permissions, data, expected_response, status_code, num_queries, obj_count):
    """
    Testing :py:meth:`system_preferences.views.LabelViewSet.create` method.
    """

    user = user_with_permissions([("system_preferences", "label")])

    with assertNumQueries(num_queries):
        url = reverse("system_preferences:label-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = LabelViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert Label.objects.count() == obj_count


@pytest.mark.django_db
def test_label_retrieve(api_rf, label_factory, user_with_permissions):
    """
    Testing :py:meth:`system_preferences.views.LabelViewSet.retrieve` method.
    """

    user = user_with_permissions([("system_preferences", "label")])
    label = label_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse("system_preferences:label-detail", kwargs={"pk": label.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = LabelViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=label.id)

    assert response.status_code == 200

    assert response.data.keys() == {"id", "name", "items_count"}


@pytest.mark.parametrize(
    "data",
    ({"name": "Building"}, {"name": "Society"}),
)
@pytest.mark.django_db
def test_label_update(api_rf, label_factory, user_with_permissions, data):
    """
    Testing :py:meth:`system_preferences.views.LabelViewSet.partial_update` method.
    """

    user = user_with_permissions([("system_preferences", "label")])
    label = label_factory(subscription=user.associated_subscription)

    with assertNumQueries(5):
        url = reverse("system_preferences:label-detail", kwargs={"pk": label.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = LabelViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=label.id)

    assert response.status_code == 200
    assert response.data["name"] == data["name"]


@pytest.mark.django_db
def test_label_delete(api_rf, label_factory, user_with_permissions):
    """
    Testing :py:meth:`system_preferences.views.LabelViewSet.delete` method.
    """

    user = user_with_permissions([("system_preferences", "label")])
    label = label_factory(subscription=user.associated_subscription)

    with assertNumQueries(8):
        url = reverse("system_preferences:label-detail", kwargs={"pk": label.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = LabelViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=label.id)

    assert response.status_code == 204

    assert Label.objects.count() == 0
