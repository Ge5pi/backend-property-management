import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from tenant.views import ChargeViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 10),
        ({"ordering": "created_at"}, [0, 1, 2], 10),
        ({"ordering": "-created_at"}, [2, 1, 0], 10),
        ({"ordering": "title"}, [1, 2, 0], 10),
        ({"ordering": "-title"}, [0, 2, 1], 10),
        ({"ordering": "amount"}, [2, 0, 1], 10),
        ({"ordering": "-amount"}, [1, 0, 2], 10),
        ({"ordering": "status"}, [2, 0, 1], 10),
        ({"ordering": "-status"}, [1, 0, 2], 10),
        ({"status": "VERIFIED"}, [1], 10),
        ({"invoice": 0}, [0], 11),
        ({"parent_property": 0}, [2, 1, 0], 11),
        ({"unit": 0}, [2, 1, 0], 11),
        ({"created_at__gte": "2023-01-02"}, [2, 1], 10),
        ({"created_at__lte": "2023-01-04"}, [1, 0], 10),
    ),
)
@pytest.mark.django_db
def test_charge_list(
    api_rf,
    tenant_user_with_permissions,
    charge_factory,
    query_params,
    index_result,
    num_queries,
    freezer,
    invoice_factory,
):
    """
    Testing :py:meth:`tenant.views.ChargeViewSet.list` method.
    """
    user, lease = tenant_user_with_permissions([("accounting", "charge")])
    invoice = invoice_factory(lease=lease, subscription=user.associated_subscription)

    if "invoice" in query_params:
        query_params["invoice"] = invoice.id

    if "parent_property" in query_params:
        query_params["parent_property"] = lease.unit.parent_property.id

    if "unit" in query_params:
        query_params["unit"] = lease.unit.id

    freezer.move_to("2023-01-01 00:00:00")
    instance_1 = charge_factory(
        title="Perform such current however.",
        amount="1000.00",
        status="UNPAID",
        tenant=lease.primary_tenant,
        unit=lease.unit,
        parent_property=lease.unit.parent_property,
        subscription=user.associated_subscription,
        invoice=invoice,
    )
    freezer.move_to("2023-01-03 00:00:00")
    instance_2 = charge_factory(
        title="Almost affect one theory",
        amount="2000.00",
        status="VERIFIED",
        tenant=lease.primary_tenant,
        unit=lease.unit,
        parent_property=lease.unit.parent_property,
        subscription=user.associated_subscription,
    )
    freezer.move_to("2023-01-05 00:00:00")
    instance_3 = charge_factory(
        title="Amount they collection those city tend able.",
        description="Accept tree public hit race",
        amount="500.00",
        status="NOT_VERIFIED",
        tenant=lease.primary_tenant,
        unit=lease.unit,
        parent_property=lease.unit.parent_property,
        subscription=user.associated_subscription,
    )
    charge_factory()

    charges = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("tenant:charge-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = ChargeViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [charges[i] for i in index_result]


@pytest.mark.django_db
def test_charge_retrieve(api_rf, charge_factory, tenant_user_with_permissions):
    """
    Testing :py:meth:`tenant.views.ChargeViewSet.retrieve` method.
    """

    user, lease = tenant_user_with_permissions([("accounting", "charge")])
    charge = charge_factory(subscription=user.associated_subscription, tenant=lease.primary_tenant)

    with assertNumQueries(10):
        url = reverse("tenant:charge-detail", kwargs={"pk": charge.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = ChargeViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=charge.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "slug",
        "title",
        "description",
        "charge_type",
        "get_charge_type_display",
        "status",
        "get_status_display",
        "amount",
        "gl_account",
        "tenant",
        "parent_property",
        "unit",
        "notes",
        "created_at",
        "parent_charge",
        "invoice",
        "property_name",
        "unit_name",
        "tenant_first_name",
        "tenant_last_name",
    }
