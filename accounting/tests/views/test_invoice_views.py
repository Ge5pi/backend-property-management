from datetime import datetime

import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from accounting.views import InvoiceViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 9),
        ({"ordering": "due_date"}, [0, 2, 1], 9),
        ({"ordering": "-due_date"}, [1, 2, 0], 9),
        ({"ordering": "rent_amount"}, [2, 0, 1], 9),
        ({"ordering": "-rent_amount"}, [1, 0, 2], 9),
        ({"search": "Property 1"}, [0], 5),
        ({"search": "Unit 1"}, [1], 5),
        ({"parent_property": True}, [0], 6),
        ({"unit": True}, [1], 6),
        ({"due_date": "2021-01-03"}, [1], 5),
        ({"arrear_of": True}, [1], 6),
        ({"status": "VERIFIED"}, [2], 5),
        ({"created_at__gte": "2023-01-02"}, [2, 1], 7),
        ({"created_at__lte": "2023-01-04"}, [1, 0], 7),
    ),
)
@pytest.mark.django_db
def test_invoice_list(
    api_rf,
    user_with_permissions,
    property_factory,
    unit_factory,
    invoice_factory,
    query_params,
    index_result,
    num_queries,
    freezer,
):
    """
    Testing :py:meth:`accounting.views.InvoiceViewSet.list` method.
    """
    user = user_with_permissions([("accounting", "invoice")])
    prop = property_factory(name="Property 1")
    unit = unit_factory(name="Unit 1")

    if query_params.get("parent_property", False):
        query_params["parent_property"] = prop.id

    if query_params.get("unit", False):
        query_params["unit"] = unit.id

    freezer.move_to("2023-01-01 00:00:00")
    instance_1 = invoice_factory(
        due_date=datetime(2021, 1, 1),
        rent_amount="1000.00",
        parent_property=prop,
        unit__name="Govt. Agencies",
        status="UNPAID",
        subscription=user.associated_subscription,
    )
    freezer.move_to("2023-01-03 00:00:00")
    instance_2 = invoice_factory(
        due_date="2021-01-03",
        rent_amount="2000.00",
        unit=unit,
        parent_property__name="Williams Track 307",
        subscription=user.associated_subscription,
        arrear_of=instance_1,
        status="NOT_VERIFIED",
    )
    freezer.move_to("2023-01-05 00:00:00")
    instance_3 = invoice_factory(
        due_date="2021-01-02",
        rent_amount="500.00",
        unit__name="General Block",
        parent_property__name="Miguel Shore 3872",
        subscription=user.associated_subscription,
        status="VERIFIED",
    )
    invoice_factory()

    invoices = [instance_1.id, instance_2.id, instance_3.id]

    if query_params.get("arrear_of", False):
        query_params["arrear_of"] = instance_1.id

    with assertNumQueries(num_queries):
        url = reverse("accounting:invoice-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = InvoiceViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [invoices[i] for i in index_result]


@pytest.mark.django_db
def test_invoice_retrieve(api_rf, invoice_factory, user_with_permissions):
    """
    Testing :py:meth:`accounting.views.InvoiceViewSet.retrieve` method.
    """

    user = user_with_permissions([("accounting", "invoice")])
    invoice = invoice_factory(
        subscription=user.associated_subscription,
    )

    with assertNumQueries(5):
        url = reverse("accounting:invoice-detail", kwargs={"pk": invoice.id})
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
def test_invoice_update(api_rf, invoice_factory, user_with_permissions):
    """
    Testing :py:meth:`accounting.views.InvoiceViewSet.partial_update` method.
    """

    user = user_with_permissions([("accounting", "invoice")])
    invoice = invoice_factory(subscription=user.associated_subscription)
    data = {"status": "VERIFIED"}

    with assertNumQueries(6):
        url = reverse("accounting:invoice-detail", kwargs={"pk": invoice.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = InvoiceViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=invoice.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value
