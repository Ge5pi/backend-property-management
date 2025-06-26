import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from accounting.models import Account
from accounting.views import AccountViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"ordering": "bank_name"}, [0, 2, 1], 3),
        ({"ordering": "-bank_name"}, [1, 2, 0], 3),
        ({"ordering": "account_title"}, [1, 2, 0], 3),
        ({"ordering": "-account_title"}, [0, 2, 1], 3),
        ({"ordering": "account_number"}, [1, 0, 2], 3),
        ({"ordering": "-account_number"}, [2, 0, 1], 3),
        ({"search": "Kevin Smith"}, [0], 3),
        ({"search": "4811933399"}, [1], 3),
        ({"search": "Chase"}, [2], 3),
    ),
)
@pytest.mark.django_db
def test_account_list(
    api_rf,
    user_with_permissions,
    account_factory,
    query_params,
    index_result,
    num_queries,
):
    """
    Testing :py:meth:`accounting.views.AccountViewSet.list` method.
    """
    user = user_with_permissions([("accounting", "account")])

    instance_1 = account_factory(
        bank_name="Bank of America",
        account_title="Kevin Smith",
        account_number="6287556830",
        subscription=user.associated_subscription,
    )
    instance_2 = account_factory(
        bank_name="Wells Fargo",
        account_title="James Ramirez",
        account_number="4811933399",
        subscription=user.associated_subscription,
    )
    instance_3 = account_factory(
        bank_name="Chase",
        account_title="John Maxwell",
        account_number="7100665416",
        subscription=user.associated_subscription,
    )
    account_factory()

    accounts = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("accounting:account-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = AccountViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [accounts[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "bank_name": ["This field is required."],
                "branch_name": ["This field is required."],
                "branch_code": ["This field is required."],
                "account_title": ["This field is required."],
                "account_number": ["This field is required."],
                "iban": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "bank_name": "Bank of America",
                "branch_name": "New York",
                "branch_code": "123456",
                "account_title": "James Ramirez",
                "account_number": "1234567890",
                "iban": "1234567890",
                "address": "New York",
                "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "notes": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            },
            None,
            201,
            3,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_account_create(api_rf, user_with_permissions, data, expected_response, status_code, num_queries, obj_count):
    """
    Testing :py:meth:`accounting.views.AccountViewSet.create` method.
    """

    user = user_with_permissions([("accounting", "account")])

    with assertNumQueries(num_queries):
        url = reverse("accounting:account-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = AccountViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert Account.objects.count() == obj_count


@pytest.mark.django_db
def test_account_retrieve(api_rf, account_factory, user_with_permissions):
    """
    Testing :py:meth:`accounting.views.AccountViewSet.retrieve` method.
    """

    user = user_with_permissions([("accounting", "account")])
    account = account_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse("accounting:account-detail", kwargs={"pk": account.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = AccountViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=account.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "bank_name",
        "branch_name",
        "branch_code",
        "account_title",
        "account_number",
        "iban",
        "address",
        "description",
        "notes",
    }


@pytest.mark.django_db
def test_account_update(api_rf, account_factory, user_with_permissions):
    """
    Testing :py:meth:`accounting.views.AccountViewSet.partial_update` method.
    """

    user = user_with_permissions([("accounting", "account")])
    account = account_factory(subscription=user.associated_subscription)
    data = {
        "bank_name": "Bank of America",
        "branch_name": "New York",
        "branch_code": "123456",
        "account_title": "James Ramirez",
        "account_number": "1234567890",
        "iban": "1234567890",
        "address": "New York",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "notes": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    }

    with assertNumQueries(4):
        url = reverse("accounting:account-detail", kwargs={"pk": account.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = AccountViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=account.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_account_delete(api_rf, account_factory, user_with_permissions):
    """
    Testing :py:meth:`accounting.views.AccountViewSet.delete` method.
    """

    user = user_with_permissions([("accounting", "account")])
    account = account_factory(subscription=user.associated_subscription)

    with assertNumQueries(6):
        url = reverse("accounting:account-detail", kwargs={"pk": account.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = AccountViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=account.id)

    assert response.status_code == 204

    assert Account.objects.count() == 0
