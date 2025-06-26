import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from property.models import Unit
from property.views import UnitViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 26),
        ({"parent_property": True}, [2], 13),
        ({"unit_type": True}, [2], 13),
        ({"is_occupied": True}, [0], 12),
        ({"search": "John Property"}, [0], 12),
        ({"search": "2370 Box 4044"}, [1], 12),
        ({"search": "unt-2"}, [1], 12),
    ),
)
@pytest.mark.django_db
def test_unit_list(
    api_rf,
    user_with_permissions,
    unit_factory,
    unit_type_factory,
    query_params,
    index_result,
    num_queries,
    lease_factory,
):
    """
    Testing :py:meth:`property.views.UnitViewSet.list` method.
    """
    user = user_with_permissions([("property", "unit")])
    unit_type = unit_type_factory(subscription=user.associated_subscription)

    instance_1 = unit_factory(
        name="John Property", address="Unit 0472 Box 2921", subscription=user.associated_subscription
    )
    instance_2 = unit_factory(
        name="Jane Property", address="Unit 2370 Box 4044", subscription=user.associated_subscription
    )
    instance_3 = unit_factory(
        name="Doe Property",
        address="13579 Kenneth Glens",
        subscription=user.associated_subscription,
        unit_type=unit_type,
        parent_property=unit_type.parent_property,
    )
    unit_factory()
    lease_factory(unit=instance_1, status="ACTIVE", rental_application__applicant__unit=instance_1)

    if query_params.get("parent_property"):
        query_params["parent_property"] = unit_type.parent_property.id

    if query_params.get("unit_type"):
        query_params["unit_type"] = unit_type.id

    if query_params.get("search") and query_params.get("search").startswith("unt-"):
        query_params["search"] = f"unt-{instance_2.id}"

    units = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("property:unit-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = UnitViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [units[i] for i in index_result]
    assert response.data[0].keys() == {
        "id",
        "name",
        "slug",
        "unit_type",
        "is_occupied",
        "market_rent",
        "lease_start_date",
        "lease_end_date",
        "cover_picture",
        "cover_picture_id",
        "property_name",
        "tenant_first_name",
        "tenant_last_name",
        "unit_type_name",
        "unit_type_bed_rooms",
        "unit_type_bath_rooms",
    }


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "unit_type": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "name": "name",
                "market_rent": "1.00",
                "future_market_rent": "1.00",
                "effective_date": "2021-01-01",
                "application_fee": "1.00",
                "tags": [],
                "estimate_turn_over_cost": "1.00",
                "address": "address",
                "ready_for_show_on": "2021-01-01",
                "virtual_showing_available": True,
                "utility_bills": True,
                "utility_bills_date": "2021-01-01",
                "lock_box": "lock_box",
                "description": "description",
                "non_revenues_status": True,
                "balance": "1.00",
                "total_charges": "1.00",
                "total_credit": "1.00",
                "due_amount": "1.00",
                "total_payable": "1.00",
            },
            None,
            201,
            15,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_unit_create(
    api_rf,
    unit_type_factory,
    tag_factory,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`property.views.UnitViewSet.create` method.
    """

    user = user_with_permissions([("property", "unit")])
    tag = tag_factory(subscription=user.associated_subscription)

    if status_code == 201:
        data["unit_type"] = unit_type_factory().id
        data["tags"] = [tag.id]

    with assertNumQueries(num_queries):
        url = reverse("property:unit-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = UnitViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert Unit.objects.count() == obj_count


@pytest.mark.django_db
def test_unit_retrieve(api_rf, unit_factory, user_with_permissions):
    """
    Testing :py:meth:`property.views.UnitViewSet.retrieve` method.
    """

    user = user_with_permissions([("property", "unit")])
    unit = unit_factory(subscription=user.associated_subscription)

    with assertNumQueries(10):
        url = reverse("property:unit-detail", kwargs={"pk": unit.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = UnitViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=unit.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "name",
        "slug",
        "unit_type",
        "market_rent",
        "future_market_rent",
        "effective_date",
        "application_fee",
        "tags",
        "estimate_turn_over_cost",
        "address",
        "ready_for_show_on",
        "virtual_showing_available",
        "utility_bills",
        "utility_bills_date",
        "lock_box",
        "description",
        "non_revenues_status",
        "balance",
        "total_charges",
        "total_credit",
        "due_amount",
        "total_payable",
        "parent_property",
        "unit_type_name",
        "cover_picture",
        "cover_picture_id",
        "is_occupied",
        "lease_id",
        "tenant_id",
        "tenant_first_name",
        "tenant_last_name",
    }


@pytest.mark.django_db
def test_unit_update(api_rf, unit_factory, user_with_permissions, tag_factory):
    """
    Testing :py:meth:`property.views.UnitViewSet.partial_update` method.
    """

    user = user_with_permissions([("property", "unit")])
    tag = tag_factory(subscription=user.associated_subscription)
    unit = unit_factory(subscription=user.associated_subscription)
    data = {
        "name": "name",
        "unit_type": unit.unit_type.id,
        "market_rent": "1.00",
        "future_market_rent": "1.00",
        "effective_date": "2021-01-01",
        "application_fee": "1.00",
        "tags": [tag.id],
        "estimate_turn_over_cost": "1.00",
        "address": "address",
        "ready_for_show_on": "2021-01-01",
        "virtual_showing_available": True,
        "utility_bills": True,
        "utility_bills_date": "2021-01-01",
        "lock_box": "lock_box",
        "description": "description",
        "non_revenues_status": True,
        "balance": "1.00",
        "total_charges": "1.00",
        "total_credit": "1.00",
        "due_amount": "1.00",
        "total_payable": "1.00",
        "parent_property": unit.parent_property.id,
    }

    with assertNumQueries(16):
        url = reverse("property:unit-detail", kwargs={"pk": unit.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = UnitViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=unit.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_unit_delete(api_rf, unit_factory, user_with_permissions):
    """
    Testing :py:meth:`property.views.UnitViewSet.delete` method.
    """

    user = user_with_permissions([("property", "unit")])
    unit = unit_factory(subscription=user.associated_subscription)

    with assertNumQueries(20):
        url = reverse("property:unit-detail", kwargs={"pk": unit.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = UnitViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=unit.id)

    assert response.status_code == 204

    assert Unit.objects.count() == 0
