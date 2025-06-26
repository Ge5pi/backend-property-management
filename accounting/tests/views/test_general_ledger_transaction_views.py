import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from accounting.views import GeneralLedgerTransactionViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"ordering": "transaction_type"}, [1, 2, 0], 3),
        ({"ordering": "-transaction_type"}, [0, 1, 2], 3),
        ({"ordering": "amount"}, [0, 1, 2], 3),
        ({"ordering": "-amount"}, [2, 1, 0], 3),
        ({"search": "unit"}, [0], 3),
        ({"transaction_type": "CREDIT"}, [2, 1], 3),
        ({"gl_account": True}, [2], 4),
        ({"gl_account__account_type": "INCOME"}, [0], 3),
    ),
)
@pytest.mark.django_db
def test_general_ledger_transaction_list(
    api_rf, user_with_permissions, general_ledger_transaction_factory, query_params, index_result, num_queries
):
    """
    Testing :py:meth:`accounting.views.GeneralLedgerTransactionViewSet.list` method.
    """
    user = user_with_permissions([("accounting", "generalledgertransaction")])

    instance_1 = general_ledger_transaction_factory(
        subscription=user.associated_subscription,
        gl_account__account_holder_content_type__model="unit",
        gl_account__account_type="INCOME",
        transaction_type="DEBIT",
        amount=100,
    )
    instance_2 = general_ledger_transaction_factory(
        subscription=user.associated_subscription,
        gl_account__account_holder_content_type__model="owner",
        transaction_type="CREDIT",
        amount=200,
    )
    instance_3 = general_ledger_transaction_factory(
        subscription=user.associated_subscription,
        gl_account__account_holder_content_type__model="vendor",
        transaction_type="CREDIT",
        amount=300,
    )
    general_ledger_transaction_factory()

    if query_params.get("gl_account"):
        query_params["gl_account"] = instance_3.gl_account.id

    general_ledger_transactions = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("accounting:general-ledger-transaction-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = GeneralLedgerTransactionViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [general_ledger_transactions[i] for i in index_result]


@pytest.mark.django_db
def test_general_ledger_transaction_retrieve(api_rf, general_ledger_transaction_factory, user_with_permissions):
    """
    Testing :py:meth:`accounting.views.GeneralLedgerTransactionViewSet.retrieve` method.
    """

    user = user_with_permissions([("accounting", "generalledgertransaction")])
    general_ledger_transaction = general_ledger_transaction_factory(
        subscription=user.associated_subscription,
    )

    with assertNumQueries(3):
        url = reverse("accounting:general-ledger-transaction-detail", kwargs={"pk": general_ledger_transaction.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = GeneralLedgerTransactionViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=general_ledger_transaction.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "transaction_type",
        "get_transaction_type_display",
        "description",
        "amount",
        "gl_account",
        "created_at",
    }
