import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from system_preferences.models import InventoryItemType
from system_preferences.views import InventoryItemTypeViewSet


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
def test_inventory_item_type_list(
    api_rf, user_with_permissions, inventory_item_type_factory, query_params, index_result
):
    """
    Testing :py:meth:`system_preferences.views.InventoryItemTypeViewSet.list` method.
    """
    user = user_with_permissions([("system_preferences", "inventoryitemtype")])

    instance_1 = inventory_item_type_factory(name="Building", subscription=user.associated_subscription)
    instance_2 = inventory_item_type_factory(name="Apartment", subscription=user.associated_subscription)
    instance_3 = inventory_item_type_factory(name="Shop", subscription=user.associated_subscription)
    inventory_item_type_factory()

    inventory_item_types = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(3):
        url = reverse("system_preferences:inventory-item-type-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = InventoryItemTypeViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [inventory_item_types[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        ({}, {"name": ["This field is required."]}, 400, 2, 0),
        ({"name": ""}, {"name": ["This field may not be blank."]}, 400, 2, 0),
        ({"name": "Building"}, None, 201, 4, 1),
    ),
)
@pytest.mark.django_db
def test_inventory_item_type_create(
    api_rf, user_with_permissions, data, expected_response, status_code, num_queries, obj_count
):
    """
    Testing :py:meth:`system_preferences.views.InventoryItemTypeViewSet.create` method.
    """
    user = user_with_permissions([("system_preferences", "inventoryitemtype")])

    with assertNumQueries(num_queries):
        url = reverse("system_preferences:inventory-item-type-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = InventoryItemTypeViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert InventoryItemType.objects.count() == obj_count


@pytest.mark.django_db
def test_inventory_item_type_retrieve(api_rf, inventory_item_type_factory, user_with_permissions):
    """
    Testing :py:meth:`system_preferences.views.InventoryItemTypeViewSet.retrieve` method.
    """
    user = user_with_permissions([("system_preferences", "inventoryitemtype")])
    inventory_item_type = inventory_item_type_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse(
            "system_preferences:inventory-item-type-detail",
            kwargs={"pk": inventory_item_type.id},
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = InventoryItemTypeViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=inventory_item_type.id)

    assert response.status_code == 200

    assert response.data.keys() == {"id", "name", "items_count"}


@pytest.mark.parametrize(
    "data",
    ({"name": "Building"}, {"name": "Society"}),
)
@pytest.mark.django_db
def test_inventory_item_type_update(api_rf, inventory_item_type_factory, user_with_permissions, data):
    """
    Testing :py:meth:`system_preferences.views.InventoryItemTypeViewSet.partial_update` method.
    """
    user = user_with_permissions([("system_preferences", "inventoryitemtype")])
    inventory_item_type = inventory_item_type_factory(subscription=user.associated_subscription)

    with assertNumQueries(5):
        url = reverse(
            "system_preferences:inventory-item-type-detail",
            kwargs={"pk": inventory_item_type.id},
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = InventoryItemTypeViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=inventory_item_type.id)

    assert response.status_code == 200
    assert response.data["name"] == data["name"]


@pytest.mark.django_db
def test_inventory_item_type_delete(api_rf, inventory_item_type_factory, user_with_permissions):
    """
    Testing :py:meth:`system_preferences.views.InventoryItemTypeViewSet.delete` method.
    """
    user = user_with_permissions([("system_preferences", "inventoryitemtype")])
    inventory_item_type = inventory_item_type_factory(subscription=user.associated_subscription)

    with assertNumQueries(5):
        url = reverse(
            "system_preferences:inventory-item-type-detail",
            kwargs={"pk": inventory_item_type.id},
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = InventoryItemTypeViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=inventory_item_type.id)

    assert response.status_code == 204

    assert InventoryItemType.objects.count() == 0
