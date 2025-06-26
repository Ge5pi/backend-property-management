import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from accounting.models import Payment
from accounting.views import PaymentViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 5),
        ({"payment_date__lte": "2021-07-01"}, [1, 0], 5),
        ({"payment_date__gte": "2021-05-01"}, [2, 1], 5),
        ({"invoice__status": "VERIFIED"}, [2], 5),
        ({"search": "John"}, [2, 0], 5),
        ({"search": "300"}, [2], 5),
        ({"ordering": "payment_date"}, [0, 1, 2], 5),
        ({"ordering": "-payment_date"}, [2, 1, 0], 5),
        ({"ordering": "amount"}, [0, 1, 2], 5),
        ({"ordering": "-amount"}, [2, 1, 0], 5),
        ({"ordering": "invoice__status"}, [0, 1, 2], 5),
        ({"ordering": "-invoice__status"}, [2, 1, 0], 5),
        ({"invoice__lease__rental_application__applicant": True}, [2], 6),
    ),
)
@pytest.mark.django_db
def test_payment_list(
    api_rf,
    user_with_permissions,
    invoice_factory,
    account_factory,
    payment_factory,
    query_params,
    index_result,
    num_queries,
):
    """
    Testing :py:meth:`accounting.views.PaymentViewSet.list` method.
    """
    user = user_with_permissions([("accounting", "payment")])

    invoice_1 = invoice_factory(status="REJECTED")
    invoice_2 = invoice_factory(status="UNPAID")
    invoice_3 = invoice_factory(status="VERIFIED")
    account_1 = account_factory(account_title="John Maxwell")
    account_2 = account_factory(account_title="James Ramirez")
    account_3 = account_factory(account_title="John Doe")

    if query_params.get("search") and query_params["search"] == "inv-1":
        query_params["invoice__slug"] = f"inv-{invoice_1.id}"

    instance_1 = payment_factory(
        payment_date="2021-01-01",
        amount="100.00",
        invoice=invoice_1,
        account=account_1,
        subscription=user.associated_subscription,
    )
    instance_2 = payment_factory(
        payment_date="2021-06-01",
        amount="200.00",
        invoice=invoice_2,
        account=account_2,
        subscription=user.associated_subscription,
    )
    instance_3 = payment_factory(
        payment_date="2021-12-01",
        amount="300.00",
        invoice=invoice_3,
        account=account_3,
        subscription=user.associated_subscription,
    )
    payment_factory()

    if query_params.get("invoice__lease__rental_application__applicant", False):
        query_params["invoice__lease__rental_application__applicant"] = (
            instance_3.invoice.lease.rental_application.applicant.id
        )

    payments = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("accounting:payment-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = PaymentViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [payments[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "invoice": ["This field is required."],
                "amount": ["This field is required."],
                "payment_method": ["This field is required."],
                "payment_date": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "invoice": 1,
                "amount": "100.00",
                "payment_method": "BANK_TRANSFER",
                "payment_date": "2023-01-01",
                "remarks": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "account": 1,
            },
            None,
            201,
            6,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_payment_create(
    api_rf,
    invoice_factory,
    account_factory,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`accounting.views.PaymentViewSet.create` method.
    """

    user = user_with_permissions([("accounting", "payment")])
    invoice = invoice_factory()
    account = account_factory()

    if status_code == 201:
        data["invoice"] = invoice.id
        data["account"] = account.id

    with assertNumQueries(num_queries):
        url = reverse("accounting:payment-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = PaymentViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert Payment.objects.count() == obj_count


@pytest.mark.django_db
def test_payment_retrieve(api_rf, payment_factory, user_with_permissions):
    """
    Testing :py:meth:`accounting.views.PaymentViewSet.retrieve` method.
    """

    user = user_with_permissions([("accounting", "payment")])
    payment = payment_factory(subscription=user.associated_subscription)

    with assertNumQueries(5):
        url = reverse("accounting:payment-detail", kwargs={"pk": payment.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = PaymentViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=payment.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "invoice",
        "amount",
        "payment_method",
        "get_payment_method_display",
        "payment_date",
        "status",
        "get_status_display",
        "remarks",
        "notes",
        "account",
        "created_at",
        "invoice_slug",
    }


@pytest.mark.django_db
def test_payment_update(api_rf, payment_factory, tenant_factory, unit_factory, user_with_permissions):
    """
    Testing :py:meth:`accounting.views.PaymentViewSet.partial_update` method.
    """

    user = user_with_permissions([("accounting", "payment")])
    payment = payment_factory(subscription=user.associated_subscription)
    data = {
        "invoice": payment.invoice.id,
        "amount": "100.00",
        "payment_method": "BANK_TRANSFER",
        "payment_date": "2023-01-01",
        "remarks": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "account": payment.account.id,
    }

    with assertNumQueries(9):
        url = reverse("accounting:payment-detail", kwargs={"pk": payment.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = PaymentViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=payment.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value
