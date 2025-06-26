import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from accounting.views import GeneralLedgerAccountViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"ordering": "account_holder_content_type__model"}, [1, 0, 2], 3),
        ({"ordering": "-account_holder_content_type__model"}, [2, 0, 1], 3),
        ({"ordering": "account_type"}, [0, 1, 2], 3),
        ({"ordering": "-account_type"}, [2, 1, 0], 3),
        ({"ordering": "sub_account_type"}, [2, 1, 0], 3),
        ({"ordering": "-sub_account_type"}, [0, 1, 2], 3),
        ({"search": "unit"}, [0], 3),
        ({"account_type": "EQUITY"}, [1], 3),
        ({"sub_account_type": "CURRENT_LIABILITY"}, [2], 3),
    ),
)
@pytest.mark.django_db
def test_general_ledger_account_list(
    api_rf, user_with_permissions, general_ledger_account_factory, query_params, index_result, num_queries
):
    """
    Testing :py:meth:`accounting.views.GeneralLedgerAccountViewSet.list` method.
    """
    user = user_with_permissions([("accounting", "generalledgeraccount")])

    instance_1 = general_ledger_account_factory(
        subscription=user.associated_subscription,
        account_holder_content_type__model="unit",
        account_type="ASSET",
        sub_account_type="RECEIVABLES",
    )
    instance_2 = general_ledger_account_factory(
        subscription=user.associated_subscription,
        account_holder_content_type__model="owner",
        account_type="EQUITY",
        sub_account_type="DIRECT_INCOME",
    )
    instance_3 = general_ledger_account_factory(
        subscription=user.associated_subscription,
        account_holder_content_type__model="vendor",
        account_type="INCOME",
        sub_account_type="CURRENT_LIABILITY",
    )
    general_ledger_account_factory()

    general_ledger_accounts = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("accounting:general-ledger-account-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = GeneralLedgerAccountViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [general_ledger_accounts[i] for i in index_result]


@pytest.mark.django_db
def test_general_ledger_account_retrieve(api_rf, general_ledger_account_factory, user_with_permissions):
    """
    Testing :py:meth:`accounting.views.GeneralLedgerAccountViewSet.retrieve` method.
    """

    user = user_with_permissions([("accounting", "generalledgeraccount")])
    general_ledger_account = general_ledger_account_factory(
        subscription=user.associated_subscription,
    )

    with assertNumQueries(3):
        url = reverse("accounting:general-ledger-account-detail", kwargs={"pk": general_ledger_account.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = GeneralLedgerAccountViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=general_ledger_account.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "account_holder_content_type",
        "account_holder_object_id",
        "account_type",
        "get_account_type_display",
        "sub_account_type",
        "get_sub_account_type_display",
        "created_at",
        "account_holder_content_type_name",
    }
