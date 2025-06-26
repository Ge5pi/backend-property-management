import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from system_preferences.models import InventoryLocation
from system_preferences.views import InventoryLocationViewSet


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
def test_inventory_location_list(
    api_rf, user_with_permissions, inventory_location_factory, query_params, index_result
):
    """
    Testing :py:meth:`system_preferences.views.InventoryLocationViewSet.list` method.
    """
    user = user_with_permissions([("system_preferences", "inventorylocation")])

    instance_1 = inventory_location_factory(name="Building", subscription=user.associated_subscription)
    instance_2 = inventory_location_factory(name="Apartment", subscription=user.associated_subscription)
    instance_3 = inventory_location_factory(name="Shop", subscription=user.associated_subscription)
    inventory_location_factory()

    inventory_locations = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(3):
        url = reverse("system_preferences:inventory-location-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = InventoryLocationViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [inventory_locations[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        ({}, {"name": ["This field is required."]}, 400, 2, 0),
        ({"name": ""}, {"name": ["This field may not be blank."]}, 400, 2, 0),
        ({"name": "Building"}, None, 201, 4, 1),
    ),
)
@pytest.mark.django_db
def test_inventory_location_create(
    api_rf, user_with_permissions, data, expected_response, status_code, num_queries, obj_count
):
    """
    Testing :py:meth:`system_preferences.views.InventoryLocationViewSet.create` method.
    """
    user = user_with_permissions([("system_preferences", "inventorylocation")])

    with assertNumQueries(num_queries):
        url = reverse("system_preferences:inventory-location-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = InventoryLocationViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert InventoryLocation.objects.count() == obj_count


@pytest.mark.django_db
def test_inventory_location_retrieve(api_rf, inventory_location_factory, user_with_permissions):
    """
    Testing :py:meth:`system_preferences.views.InventoryLocationViewSet.retrieve` method.
    """
    user = user_with_permissions([("system_preferences", "inventorylocation")])
    inventory_location = inventory_location_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse(
            "system_preferences:inventory-location-detail",
            kwargs={"pk": inventory_location.id},
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = InventoryLocationViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=inventory_location.id)

    assert response.status_code == 200

    assert response.data.keys() == {"id", "name", "items_count"}


@pytest.mark.parametrize(
    "data",
    ({"name": "Building"}, {"name": "Society"}),
)
@pytest.mark.django_db
def test_inventory_location_update(api_rf, inventory_location_factory, user_with_permissions, data):
    """
    Testing :py:meth:`system_preferences.views.InventoryLocationViewSet.partial_update` method.
    """
    user = user_with_permissions([("system_preferences", "inventorylocation")])
    inventory_location = inventory_location_factory(subscription=user.associated_subscription)

    with assertNumQueries(5):
        url = reverse(
            "system_preferences:inventory-location-detail",
            kwargs={"pk": inventory_location.id},
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = InventoryLocationViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=inventory_location.id)

    assert response.status_code == 200
    assert response.data["name"] == data["name"]


@pytest.mark.django_db
def test_inventory_location_delete(api_rf, inventory_location_factory, user_with_permissions):
    """
    Testing :py:meth:`system_preferences.views.InventoryLocationViewSet.delete` method.
    """
    user = user_with_permissions([("system_preferences", "inventorylocation")])
    inventory_location = inventory_location_factory(subscription=user.associated_subscription)

    with assertNumQueries(5):
        url = reverse(
            "system_preferences:inventory-location-detail",
            kwargs={"pk": inventory_location.id},
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = InventoryLocationViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=inventory_location.id)

    assert response.status_code == 204

    assert InventoryLocation.objects.count() == 0
