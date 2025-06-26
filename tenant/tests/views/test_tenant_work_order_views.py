import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from tenant.views import WorkOrderViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (({}, [2, 1, 0], 20),),
)
@pytest.mark.django_db
def test_work_order_list(
    api_rf,
    tenant_user_with_permissions,
    work_order_factory,
    service_request_factory,
    query_params,
    index_result,
    num_queries,
):
    """
    Testing :py:meth:`tenant.views.WorkOrderViewSet.list` method.
    """

    user, lease = tenant_user_with_permissions([("maintenance", "workorder")])
    service_request = service_request_factory(unit=lease.unit)

    instance_1 = work_order_factory(
        subscription=user.associated_subscription,
        service_request=service_request,
    )
    instance_2 = work_order_factory(
        subscription=user.associated_subscription,
        service_request=service_request,
    )
    instance_3 = work_order_factory(
        subscription=user.associated_subscription,
        service_request=service_request,
    )
    work_order_factory()

    work_order_ids = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("tenant:work_orders-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = WorkOrderViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [work_order_ids[i] for i in index_result]


@pytest.mark.django_db
def test_work_order_retrieve(api_rf, work_order_factory, service_request_factory, tenant_user_with_permissions):
    """
    Testing :py:meth:`tenant.views.WorkOrderViewSet.retrieve` method.
    """
    user, lease = tenant_user_with_permissions([("maintenance", "workorder")])
    service_request = service_request_factory(unit=lease.unit)
    work_order = work_order_factory(service_request=service_request, subscription=user.associated_subscription)

    with assertNumQueries(16):
        url = reverse("tenant:work_orders-detail", kwargs={"pk": work_order.id})
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
