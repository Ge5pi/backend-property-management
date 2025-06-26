import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from maintenance.models import Inventory
from maintenance.views import InventoryViewSet


@pytest.mark.parametrize(
    "query_params, index_result, item_type_id, location_id, vendor_id, num_queries",
    (
        ({}, [0, 1, 2], None, None, None, 3),
        ({"search": "an"}, [0], None, None, None, 3),
        ({"search": "igh"}, [1], None, None, None, 3),
        ({"search": "witc"}, [2], None, None, None, 3),
        ({"item_type": "100"}, [0, 1], 100, None, None, 5),
        ({"location": "100"}, [1, 2], None, 100, None, 5),
        ({"vendor": "100"}, [0, 2], None, None, 100, 5),
    ),
)
@pytest.mark.django_db
def test_inventory_list(
    api_rf,
    user_with_permissions,
    inventory_factory,
    vendor_factory,
    inventory_item_type_factory,
    inventory_location_factory,
    query_params,
    index_result,
    item_type_id,
    location_id,
    vendor_id,
    num_queries,
):
    """
    Testing :py:meth:`maintenance.views.InventoryViewSet.list` method.
    """

    user = user_with_permissions([("maintenance", "inventory")])

    vendor = vendor_factory(id=vendor_id) if vendor_id else None
    item_type = inventory_item_type_factory(id=item_type_id) if item_type_id else None
    location = inventory_location_factory(id=location_id) if location_id else None

    instance_1 = inventory_factory(
        name="Fan", item_type=item_type, vendor=vendor, location=None, subscription=user.associated_subscription
    )
    instance_2 = inventory_factory(
        name="Light", item_type=item_type, location=location, vendor=None, subscription=user.associated_subscription
    )
    instance_3 = inventory_factory(
        name="Switch", location=location, vendor=vendor, item_type=None, subscription=user.associated_subscription
    )
    inventory_factory()

    inventory_ids = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("maintenance:inventory-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = InventoryViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [inventory_ids[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "description": ["This field is required."],
                "part_number": ["This field is required."],
                "quantity": ["This field is required."],
                "expense_account": ["This field is required."],
                "cost": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "name": "Fan",
                "item_type": 100,
                "description": "Read line shake short term. Generation fine hotel word in religious energy.",
                "part_number": "2332",
                "vendor": 100,
                "quantity": 265229,
                "expense_account": "677121438893",
                "cost": "44.60",
                "location": 100,
                "bin_or_shelf_number": "8880",
            },
            {
                "name": "Fan",
                "item_type": 100,
                "description": "Read line shake short term. Generation fine hotel word in religious energy.",
                "part_number": "2332",
                "vendor": 100,
                "quantity": 265229,
                "expense_account": "677121438893",
                "cost": "44.60",
                "location": 100,
                "bin_or_shelf_number": "8880",
                "item_type_name": "Item Type 1",
                "location_name": "Location 1",
            },
            201,
            7,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_inventory_create(
    api_rf,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
    vendor_factory,
    inventory_item_type_factory,
    inventory_location_factory,
):
    """
    Testing :py:meth:`maintenance.views.InventoryViewSet.create` method.
    """

    user = user_with_permissions([("maintenance", "inventory")])
    vendor_factory(id=100)
    inventory_item_type_factory(id=100, name="Item Type 1")
    inventory_location_factory(id=100, name="Location 1")

    with assertNumQueries(num_queries):
        url = reverse("maintenance:inventory-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = InventoryViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code

    for key, value in expected_response.items():
        assert response.data[key] == value

    assert Inventory.objects.count() == obj_count


@pytest.mark.django_db
def test_inventory_retrieve(api_rf, inventory_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.InventoryViewSet.retrieve` method.
    """

    user = user_with_permissions([("maintenance", "inventory")])
    inventory = inventory_factory(subscription=user.associated_subscription)

    with assertNumQueries(6):
        url = reverse("maintenance:inventory-detail", kwargs={"pk": inventory.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = InventoryViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=inventory.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "name",
        "item_type",
        "description",
        "part_number",
        "vendor",
        "quantity",
        "expense_account",
        "cost",
        "location",
        "bin_or_shelf_number",
        "item_type_name",
        "location_name",
    }


@pytest.mark.django_db
def test_inventory_update(api_rf, inventory_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.InventoryViewSet.partial_update` method.
    """

    user = user_with_permissions([("maintenance", "inventory")])
    inventory = inventory_factory(subscription=user.associated_subscription)
    data = {
        "name": "Fan",
        "description": "Read line shake short term. Generation fine hotel word in religious energy.",
        "part_number": "2332",
        "expense_account": "677121438893",
        "cost": "44.60",
        "bin_or_shelf_number": "8880",
    }

    with assertNumQueries(7):
        url = reverse("maintenance:inventory-detail", kwargs={"pk": inventory.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = InventoryViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=inventory.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_inventory_delete(api_rf, inventory_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.InventoryViewSet.delete` method.
    """

    user = user_with_permissions([("maintenance", "inventory")])
    inventory = inventory_factory(subscription=user.associated_subscription)

    with assertNumQueries(9):
        url = reverse("maintenance:inventory-detail", kwargs={"pk": inventory.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = InventoryViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=inventory.id)

    assert response.status_code == 204

    assert Inventory.objects.count() == 0


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {"non_field_errors": ['Expected a list of items but got type "dict".']},
            400,
            2,
            0,
        ),
        (
            [{}],
            [
                {
                    "name": ["This field is required."],
                    "description": ["This field is required."],
                    "part_number": ["This field is required."],
                    "quantity": ["This field is required."],
                    "expense_account": ["This field is required."],
                    "cost": ["This field is required."],
                }
            ],
            400,
            2,
            0,
        ),
        (
            [
                {
                    "name": "Fan",
                    "item_type": 100,
                    "description": "Read line shake short term. Generation fine hotel word in religious energy.",
                    "part_number": "2332",
                    "vendor": 100,
                    "expense_account": "677121438893",
                    "cost": "44.60",
                    "location": 100,
                    "bin_or_shelf_number": "8880",
                    "quantity": 265229,
                },
                {
                    "name": "Light",
                    "item_type": 100,
                    "description": "Read line shake short term. Generation fine hotel word in religious energy.",
                    "part_number": "1991",
                    "vendor": 100,
                    "expense_account": "677121438891",
                    "cost": "44.60",
                    "location": 100,
                    "bin_or_shelf_number": "8880",
                    "quantity": 265229,
                },
            ],
            [
                {
                    "name": "Fan",
                    "item_type": 100,
                    "description": "Read line shake short term. Generation fine hotel word in religious energy.",
                    "part_number": "2332",
                    "vendor": 100,
                    "expense_account": "677121438893",
                    "cost": "44.60",
                    "location": 100,
                    "bin_or_shelf_number": "8880",
                    "quantity": 265229,
                    "item_type_name": "Item Type 1",
                    "location_name": "Location 1",
                },
                {
                    "name": "Light",
                    "item_type": 100,
                    "description": "Read line shake short term. Generation fine hotel word in religious energy.",
                    "part_number": "1991",
                    "vendor": 100,
                    "expense_account": "677121438891",
                    "cost": "44.60",
                    "location": 100,
                    "bin_or_shelf_number": "8880",
                    "quantity": 265229,
                    "item_type_name": "Item Type 1",
                    "location_name": "Location 1",
                },
            ],
            201,
            12,
            2,
        ),
    ),
)
@pytest.mark.django_db
def test_inventory_bulk_create(
    api_rf,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
    vendor_factory,
    inventory_item_type_factory,
    inventory_location_factory,
):
    """
    Testing :py:meth:`maintenance.views.InventoryViewSet.bulk_create` method.
    """

    user = user_with_permissions([("maintenance", "inventory")])
    vendor_factory(id=100)
    inventory_item_type_factory(id=100, name="Item Type 1")
    inventory_location_factory(id=100, name="Location 1")

    with assertNumQueries(num_queries):
        url = reverse("maintenance:inventory-bulk-create")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = InventoryViewSet.as_view({"post": "bulk_create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        if status_code == 400:
            assert response.data == expected_response
        else:
            for i, expected in zip(response.data, expected_response):
                for key, value in expected.items():
                    assert i[key] == value
    assert Inventory.objects.count() == obj_count
