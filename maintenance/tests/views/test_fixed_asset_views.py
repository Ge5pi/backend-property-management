from decimal import Decimal

import pytest
from django.urls import reverse
from pytest import approx
from pytest_django.asserts import assertNumQueries

from maintenance.models import FixedAsset
from maintenance.views import FixedAssetViewSet


@pytest.mark.parametrize(
    "query_params, index_result, unit_id, property_id, num_queries",
    (
        ({}, [2, 1, 0], None, None, 9),
        ({"search": "Hogwarts"}, [2, 1, 0], None, None, 9),
        ({"search": "Hogwarts"}, [], 100, 100, 3),
        ({"search": "Room 1"}, [2, 1, 0], None, None, 9),
        ({"unit__parent_property": "100"}, [2, 1, 0], 100, 100, 10),
        ({"unit": "100"}, [2, 1, 0], 100, None, 10),
        ({"status": "installed"}, [2, 1], None, None, 8),
        ({"ordering": "-created_at"}, [2, 1, 0], None, None, 9),
        ({"ordering": "created_at"}, [0, 1, 2], None, None, 9),
        ({"ordering": "-pk"}, [2, 1, 0], None, None, 9),
        ({"ordering": "pk"}, [0, 1, 2], None, None, 9),
        ({"ordering": "placed_in_service_date"}, [0, 1, 2], None, None, 9),
        ({"ordering": "-placed_in_service_date"}, [2, 1, 0], None, None, 9),
        ({"ordering": "warranty_expiration_date"}, [0, 1, 2], None, None, 9),
        ({"ordering": "-warranty_expiration_date"}, [2, 1, 0], None, None, 9),
    ),
)
@pytest.mark.django_db
def test_fixed_asset_list(
    api_rf,
    user_with_permissions,
    fixed_asset_factory,
    query_params,
    index_result,
    unit_factory,
    property_factory,
    unit_id,
    unit_type_factory,
    property_id,
    num_queries,
):
    """
    Testing :py:meth:`maintenance.views.FixedAssetViewSet.list` method.
    """

    user = user_with_permissions([("maintenance", "fixedasset")])
    property_name = "Hogwarts"
    unit_name = "Room 1"
    prop = property_factory(id=property_id) if property_id else property_factory(name=property_name)
    unit_type = unit_type_factory(parent_property=prop)
    unit = unit_factory(id=100, unit_type=unit_type) if unit_id else unit_factory(unit_type=unit_type, name=unit_name)

    instance_1 = fixed_asset_factory(
        status="in_storage",
        unit=unit,
        placed_in_service_date="2020-2-20",
        warranty_expiration_date="2020-2-20",
        subscription=user.associated_subscription,
    )
    instance_2 = fixed_asset_factory(
        status="installed",
        unit=unit,
        placed_in_service_date="2021-2-20",
        warranty_expiration_date="2021-2-20",
        subscription=user.associated_subscription,
    )
    instance_3 = fixed_asset_factory(
        status="installed",
        unit=unit,
        placed_in_service_date="2022-2-20",
        warranty_expiration_date="2022-2-20",
        subscription=user.associated_subscription,
    )
    fixed_asset_factory()

    fixed_asset_ids = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("maintenance:fixed_assets-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = FixedAssetViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [fixed_asset_ids[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "unit": ["This field is required."],
                "inventory_item": ["This field is required."],
                "quantity": ["This field is required."],
                "cost": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "status": "in_storage",
                "placed_in_service_date": "2020-01-01",
                "warranty_expiration_date": "2020-01-01",
                "unit": 100,
                "inventory_item": 100,
                "quantity": 9,
                "cost": "23.40",
            },
            {
                "status": "in_storage",
                "get_status_display": "In Storage",
                "placed_in_service_date": "2020-01-01",
                "warranty_expiration_date": "2020-01-01",
                "unit": 100,
                "inventory_item": 100,
                "quantity": 9,
                "cost": "23.40",
                "unit_name": "Room 1",
                "property_name": "Hogwarts",
                "inventory_location": "USA",
                "inventory_name": "Macbook Pro 2019",
                "total_cost": approx(Decimal("210.60")),
            },
            201,
            8,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_fixed_asset_create(
    api_rf,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
    unit_type_factory,
    property_factory,
    unit_factory,
    inventory_factory,
    inventory_location_factory,
):
    """
    Testing :py:meth:`maintenance.views.FixedAssetViewSet.create` method.
    """

    user = user_with_permissions([("maintenance", "fixedasset")])
    prop = property_factory(name="Hogwarts")
    unit_type = unit_type_factory(parent_property=prop)
    location = inventory_location_factory(name="USA")
    unit_factory(id=100, name="Room 1", unit_type=unit_type)
    inventory_factory(id=100, location=location, name="Macbook Pro 2019")

    with assertNumQueries(num_queries):
        url = reverse("maintenance:fixed_assets-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = FixedAssetViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code

    for key, value in expected_response.items():
        assert response.data[key] == value

    assert FixedAsset.objects.count() == obj_count


@pytest.mark.django_db
def test_fixed_asset_retrieve(api_rf, fixed_asset_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.FixedAssetViewSet.retrieve` method.
    """

    user = user_with_permissions([("maintenance", "fixedasset")])
    fixed_asset = fixed_asset_factory(subscription=user.associated_subscription)

    with assertNumQueries(7):
        url = reverse("maintenance:fixed_assets-detail", kwargs={"pk": fixed_asset.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = FixedAssetViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=fixed_asset.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "slug",
        "status",
        "get_status_display",
        "placed_in_service_date",
        "warranty_expiration_date",
        "unit",
        "inventory_item",
        "quantity",
        "cost",
        "unit_name",
        "property_name",
        "property_id",
        "inventory_name",
        "inventory_location",
        "total_cost",
    }


@pytest.mark.django_db
def test_fixed_asset_update(
    api_rf,
    fixed_asset_factory,
    user_with_permissions,
    unit_factory,
    inventory_factory,
):
    """
    Testing :py:meth:`maintenance.views.FixedAssetViewSet.partial_update` method.
    """

    user = user_with_permissions([("maintenance", "fixedasset")])
    fixed_asset = fixed_asset_factory(subscription=user.associated_subscription)
    data = {
        "status": "in_storage",
        "placed_in_service_date": "2020-01-01",
        "warranty_expiration_date": "2020-01-01",
        "unit": fixed_asset.unit.id,
        "inventory_item": fixed_asset.inventory_item.id,
        "quantity": 9,
        "cost": "23.40",
    }

    with assertNumQueries(10):
        url = reverse("maintenance:fixed_assets-detail", kwargs={"pk": fixed_asset.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = FixedAssetViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=fixed_asset.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_fixed_asset_delete(api_rf, fixed_asset_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.FixedAssetViewSet.delete` method.
    """

    user = user_with_permissions([("maintenance", "fixedasset")])
    fixed_asset = fixed_asset_factory(subscription=user.associated_subscription)

    with assertNumQueries(6):
        url = reverse("maintenance:fixed_assets-detail", kwargs={"pk": fixed_asset.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = FixedAssetViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=fixed_asset.id)

    assert response.status_code == 204

    assert FixedAsset.objects.count() == 0


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
                    "unit": ["This field is required."],
                    "inventory_item": ["This field is required."],
                    "quantity": ["This field is required."],
                }
            ],
            400,
            2,
            0,
        ),
        (
            [
                {
                    "status": "in_storage",
                    "placed_in_service_date": "2020-01-01",
                    "warranty_expiration_date": "2020-01-01",
                    "unit": 100,
                    "inventory_item": 100,
                    "quantity": 9,
                },
                {
                    "status": "installed",
                    "placed_in_service_date": "2020-01-01",
                    "warranty_expiration_date": "2020-01-01",
                    "unit": 100,
                    "inventory_item": 100,
                    "quantity": 2,
                },
            ],
            [
                {
                    "status": "in_storage",
                    "placed_in_service_date": "2020-01-01",
                    "warranty_expiration_date": "2020-01-01",
                    "unit": 100,
                    "inventory_item": 100,
                    "quantity": 9,
                    "cost": "23.40",
                },
                {
                    "status": "installed",
                    "placed_in_service_date": "2020-01-01",
                    "warranty_expiration_date": "2020-01-01",
                    "unit": 100,
                    "inventory_item": 100,
                    "quantity": 2,
                    "cost": "23.40",
                },
            ],
            201,
            10,
            2,
        ),
    ),
)
@pytest.mark.django_db
def test_fixed_asset_bulk_create(
    api_rf,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
    unit_factory,
    inventory_factory,
):
    """
    Testing :py:meth:`maintenance.views.FixedAssetViewSet.create` method.
    """

    user = user_with_permissions([("maintenance", "fixedasset")])
    unit_factory(id=100)
    inventory_factory(id=100, cost="23.40")

    with assertNumQueries(num_queries):
        url = reverse("maintenance:fixed_assets-bulk-create")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = FixedAssetViewSet.as_view({"post": "bulk_create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        if type(expected_response) is list:
            for i, expected in enumerate(expected_response):
                for key, value in expected.items():
                    assert response.data[i][key] == value
        else:
            for key, value in expected_response.items():
                assert response.data[key] == value
    assert FixedAsset.objects.count() == obj_count
