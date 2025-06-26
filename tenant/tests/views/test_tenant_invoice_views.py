from datetime import datetime

import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from accounting.models import Invoice
from tenant.views import InvoiceViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 20),
        ({"ordering": "due_date"}, [0, 2, 1], 20),
        ({"ordering": "-due_date"}, [1, 2, 0], 20),
        ({"ordering": "rent_amount"}, [2, 0, 1], 20),
        ({"ordering": "-rent_amount"}, [1, 0, 2], 20),
        ({"due_date": "2021-01-03"}, [1], 16),
        ({"arrear_of": 1}, [1], 17),
        ({"created_at__gte": "2023-01-02"}, [2, 1], 18),
        ({"created_at__lte": "2023-01-04"}, [1, 0], 18),
    ),
)
@pytest.mark.django_db
def test_invoice_list(
    api_rf, tenant_user_with_permissions, invoice_factory, query_params, index_result, num_queries, freezer
):
    """
    Testing :py:meth:`tenant.views.InvoiceViewSet.list` method.
    """
    user, lease = tenant_user_with_permissions([("accounting", "invoice")])

    freezer.move_to("2023-01-01 00:00:00")
    instance_1 = invoice_factory(
        due_date=datetime(2021, 1, 1),
        rent_amount="1000.00",
        unit=lease.unit,
        subscription=user.associated_subscription,
        lease=lease,
    )
    freezer.move_to("2023-01-03 00:00:00")
    instance_2 = invoice_factory(
        due_date="2021-01-03",
        rent_amount="2000.00",
        unit=lease.unit,
        subscription=user.associated_subscription,
        arrear_of=instance_1,
        lease=lease,
    )
    freezer.move_to("2023-01-05 00:00:00")
    instance_3 = invoice_factory(
        due_date="2021-01-02",
        rent_amount="500.00",
        unit=lease.unit,
        subscription=user.associated_subscription,
        lease=lease,
    )
    invoice_factory()

    invoices = [instance_1.id, instance_2.id, instance_3.id]

    if "arrear_of" in query_params:
        query_params["arrear_of"] = instance_1.id

    with assertNumQueries(num_queries):
        url = reverse("tenant:invoice-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = InvoiceViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [invoices[i] for i in index_result]


@pytest.mark.django_db
def test_invoice_retrieve(api_rf, invoice_factory, tenant_user_with_permissions):
    """
    Testing :py:meth:`tenant.views.InvoiceViewSet.retrieve` method.
    """

    user, lease = tenant_user_with_permissions([("accounting", "invoice")])
    invoice = invoice_factory(lease=lease, subscription=user.associated_subscription, unit=lease.unit)

    with assertNumQueries(16):
        url = reverse("tenant:invoice-detail", kwargs={"pk": invoice.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = InvoiceViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=invoice.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "slug",
        "business_information",
        "lease",
        "parent_property",
        "unit",
        "created_at",
        "interval_start_date",
        "interval_end_date",
        "due_date",
        "rent_amount",
        "payed_at",
        "payed_late_fee",
        "status",
        "get_status_display",
        "rent_cycle",
        "total_charges_amount",
        "charges_and_rent",
        "is_late_fee_applicable",
        "number_of_days_late",
        "late_fee",
        "payable_late_fee",
        "payable_amount",
        "arrears_amount",
        "arrear_of",
        "total_paid_amount",
        "payment",
        "tenant_first_name",
        "tenant_last_name",
    }


@pytest.mark.django_db
def test_invoice_mark_as_paid(api_rf, invoice_factory, tenant_user_with_permissions):
    """
    Testing :py:meth:`tenant.views.InvoiceViewSet.mark_as_paid` method.
    """

    user, lease = tenant_user_with_permissions([("accounting", "invoice")])
    lease.unit.parent_property.late_fee_policy.late_fee_type = "flat"
    lease.unit.parent_property.late_fee_policy.base_amount_fee = 100
    lease.unit.parent_property.late_fee_policy.late_fee_rate = 0.1
    lease.unit.parent_property.late_fee_policy.save()
    invoice = invoice_factory(lease=lease, subscription=user.associated_subscription, unit=lease.unit)

    with assertNumQueries(16):
        url = reverse("tenant:invoice-mark-as-paid", kwargs={"pk": invoice.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = InvoiceViewSet.as_view({"get": "mark_as_paid"})
        response = view(request, pk=invoice.id)

    assert response.status_code == 200
    assert Invoice.objects.get().status == "NOT_VERIFIED"
