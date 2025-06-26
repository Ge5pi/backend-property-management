import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from maintenance.views import WorkOrder, WorkOrderViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 9),
        ({"search": "wko-2"}, [1], 5),
        ({"search": "Doctor off store bad"}, [0], 5),
        ({"search": "West food political "}, [1], 5),
        ({"search": "INTERNAL"}, [2], 5),
        ({"status": "OPEN"}, [0], 5),
        ({"service_request": 1}, [0], 6),
        ({"ordering": "slug"}, [0, 1, 2], 9),
        ({"ordering": "-slug"}, [2, 1, 0], 9),
        ({"ordering": "job_description"}, [2, 0, 1], 9),
        ({"ordering": "-job_description"}, [1, 0, 2], 9),
        ({"ordering": "created_at"}, [0, 1, 2], 9),
        ({"ordering": "-created_at"}, [2, 1, 0], 9),
        ({"ordering": "status"}, [1, 2, 0], 9),
        ({"ordering": "-status"}, [0, 2, 1], 9),
    ),
)
@pytest.mark.django_db
def test_work_order_list(
    api_rf,
    user_with_permissions,
    work_order_factory,
    service_request_factory,
    query_params,
    index_result,
    num_queries,
):
    """
    Testing :py:meth:`maintenance.views.WorkOrderViewSet.list` method.
    """

    user = user_with_permissions([("maintenance", "workorder")])
    service_request = service_request_factory()

    instance_1 = work_order_factory(
        job_description="Doctor off store bad. Today game treat east",
        order_type="RESIDENT",
        service_request=service_request,
        status="OPEN",
        subscription=user.associated_subscription,
    )
    instance_2 = work_order_factory(
        job_description="Move test about believe the reason show it",
        vendor_instructions="'West food political medical view group cell",
        order_type="RESIDENT",
        status="ASSIGNED",
        subscription=user.associated_subscription,
    )
    instance_3 = work_order_factory(
        job_description="Anything common staff war project investment",
        order_type="INTERNAL",
        status="COMPLETED",
        subscription=user.associated_subscription,
    )
    work_order_factory()

    if query_params.get("search") == "wko-2":
        query_params["search"] = f"wko-{instance_2.id}"

    if "service_request" in query_params:
        query_params["service_request"] = instance_1.service_request.id

    work_order_ids = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("maintenance:work_orders-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = WorkOrderViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [work_order_ids[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "order_type": ["This field is required."],
                "vendor_type": ["This field is required."],
                "vendor": ["This field is required."],
                "email_vendor": ["This field is required."],
                "follow_up_date": ["This field is required."],
                "service_request": ["This field is required."],
                "request_receipt": ["This field is required."],
                "owner_approved": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "is_recurring": False,
                "cycle": "MONTHLY",
                "status": "OPEN",
                "order_type": "RESIDENT",
                "job_description": "Color theory official game.",
                "vendor_instructions": "West rock drive onto attorney",
                "vendor_trade": "PLUMBER",
                "vendor_type": 100,
                "vendor": 100,
                "email_vendor": True,
                "assign_to": 100,
                "follow_up_date": "1987-01-12",
                "service_request": 100,
                "request_receipt": False,
                "owner_approved": False,
            },
            None,
            201,
            13,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_work_order_create(
    api_rf,
    vendor_type_factory,
    vendor_factory,
    user_with_permissions,
    service_request_factory,
    unit_factory,
    unit_type_factory,
    property_factory,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    vendor_type_factory(id=100)
    vendor_factory(id=100)
    user = user_with_permissions([("maintenance", "workorder")], id=100)
    prop = property_factory(name="Fly place stage more myself")
    unit_type = unit_type_factory(parent_property=prop)
    unit = unit_factory(unit_type=unit_type)
    service_request = service_request_factory(id=100, unit=unit)

    with assertNumQueries(num_queries):
        url = reverse("maintenance:work_orders-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = WorkOrderViewSet.as_view({"post": "create"})
        response = view(request, service_request_id=service_request.id)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert WorkOrder.objects.count() == obj_count


@pytest.mark.django_db
def test_work_order_retrieve(api_rf, work_order_factory, service_request_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.WorkOrderViewSet.retrieve` method.
    """
    user = user_with_permissions([("maintenance", "workorder")])
    service_request = service_request_factory()
    work_order = work_order_factory(service_request=service_request, subscription=user.associated_subscription)
    with assertNumQueries(5):
        url = reverse("maintenance:work_orders-detail", kwargs={"pk": work_order.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = WorkOrderViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=work_order.id, service_request_id=service_request.id)

    assert response.status_code == 200
    assert response.data.keys() == {
        "id",
        "slug",
        "is_recurring",
        "cycle",
        "status",
        "order_type",
        "get_order_type_display",
        "get_status_display",
        "get_cycle_display",
        "job_description",
        "vendor_instructions",
        "vendor_trade",
        "vendor_type",
        "vendor",
        "email_vendor",
        "assign_to",
        "follow_up_date",
        "created_by",
        "created_at",
        "service_request",
        "request_receipt",
        "owner_approved",
        "property_name",
        "property_id",
        "assign_to_first_name",
        "assign_to_last_name",
        "assign_to_username",
    }


@pytest.mark.django_db
def test_work_order_update(
    api_rf,
    vendor_type_factory,
    vendor_factory,
    user_with_permissions,
    service_request_factory,
    unit_factory,
    unit_type_factory,
    property_factory,
    work_order_factory,
):
    vendor_type_factory(id=100)
    vendor_factory(id=100)
    user = user_with_permissions([("maintenance", "workorder")], id=100)
    prop = property_factory(name="Fly place stage more myself")
    unit_type = unit_type_factory(parent_property=prop)
    unit = unit_factory(unit_type=unit_type)
    service_request = service_request_factory(id=100, unit=unit)
    work_order = work_order_factory(service_request=service_request, subscription=user.associated_subscription)

    data = {
        "is_recurring": False,
        "cycle": "MONTHLY",
        "status": "OPEN",
        "order_type": "RESIDENT",
        "job_description": "Color theory official game.",
        "vendor_instructions": "West rock drive onto attorney",
        "vendor_trade": "PLUMBER",
        "vendor_type": 100,
        "vendor": 100,
        "email_vendor": True,
        "assign_to": 100,
        "follow_up_date": "1987-01-12",
        "service_request": 100,
        "request_receipt": False,
        "owner_approved": False,
    }

    with assertNumQueries(10):
        url = reverse("maintenance:work_orders-detail", kwargs={"pk": work_order.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = WorkOrderViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=work_order.id, service_request_id=service_request.id)

    assert response.status_code == 200

    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_work_order_delete(api_rf, service_request_factory, work_order_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.WorkOrderViewSet.delete` method.
    """
    user = user_with_permissions([("maintenance", "workorder")])
    service_request = service_request_factory()
    work_order = work_order_factory(service_request=service_request, subscription=user.associated_subscription)
    with assertNumQueries(5):
        url = reverse("maintenance:work_orders-detail", kwargs={"pk": work_order.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = WorkOrderViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=work_order.id, service_request_id=service_request.id)
    assert response.status_code == 204
    assert WorkOrder.objects.count() == 0
