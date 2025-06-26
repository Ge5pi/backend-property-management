import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from lease.models import RentalApplicationFinancialInformation
from lease.views import RentalApplicationFinancialInformationViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"rental_application": 0}, [0], 4),
    ),
)
@pytest.mark.django_db
def test_rental_application_financial_information_list(
    api_rf,
    user_with_permissions,
    rental_application_financial_information_factory,
    query_params,
    index_result,
    num_queries,
    rental_application_factory,
):
    """
    Testing :py:meth:`lease.views.RentalApplicationFinancialInformationViewSet.list` method.
    """
    user = user_with_permissions([("lease", "rentalapplicationfinancialinformation")])
    rental_application = rental_application_factory()
    rental_applications = [rental_application.id]
    if "rental_application" in query_params:
        query_params["rental_application"] = rental_applications[query_params["rental_application"]]

    instance_1 = rental_application_financial_information_factory(
        rental_application=rental_application, subscription=user.associated_subscription
    )
    instance_2 = rental_application_financial_information_factory(subscription=user.associated_subscription)
    instance_3 = rental_application_financial_information_factory(subscription=user.associated_subscription)
    rental_application_financial_information_factory()

    rental_application_financial_informations = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("lease:rental-application-financial-information-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = RentalApplicationFinancialInformationViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [rental_application_financial_informations[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "account_type": ["This field is required."],
                "bank": ["This field is required."],
                "account_number": ["This field is required."],
                "rental_application": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "name": "Test Name",
                "account_type": "Test Account Type",
                "bank": "Test Bank",
                "account_number": "123456789",
            },
            None,
            201,
            4,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_rental_application_financial_information_create(
    api_rf,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
    rental_application_factory,
):
    """
    Testing :py:meth:`lease.views.RentalApplicationFinancialInformationViewSet.create` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationfinancialinformation")])
    rental_application = rental_application_factory()
    if status_code == 201:
        data["rental_application"] = rental_application.id

    with assertNumQueries(num_queries):
        url = reverse("lease:rental-application-financial-information-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = RentalApplicationFinancialInformationViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert RentalApplicationFinancialInformation.objects.count() == obj_count


@pytest.mark.django_db
def test_rental_application_financial_information_retrieve(
    api_rf, rental_application_financial_information_factory, user_with_permissions
):
    """
    Testing :py:meth:`lease.views.RentalApplicationFinancialInformationViewSet.retrieve` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationfinancialinformation")])
    rental_application_financial_information = rental_application_financial_information_factory(
        subscription=user.associated_subscription
    )

    with assertNumQueries(3):
        url = reverse(
            "lease:rental-application-financial-information-detail",
            kwargs={"pk": rental_application_financial_information.id},
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = RentalApplicationFinancialInformationViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=rental_application_financial_information.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "name",
        "account_type",
        "bank",
        "account_number",
        "rental_application",
    }


@pytest.mark.django_db
def test_rental_application_financial_information_update(
    api_rf, rental_application_financial_information_factory, user_with_permissions
):
    """
    Testing :py:meth:`lease.views.RentalApplicationFinancialInformationViewSet.partial_update` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationfinancialinformation")])
    rental_application_financial_information = rental_application_financial_information_factory(
        subscription=user.associated_subscription
    )
    data = {
        "name": "Test Name",
        "account_type": "Test Account Type",
        "bank": "Test Bank",
        "account_number": "123456789",
        "rental_application": rental_application_financial_information.rental_application.id,
    }

    with assertNumQueries(5):
        url = reverse(
            "lease:rental-application-financial-information-detail",
            kwargs={"pk": rental_application_financial_information.id},
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = RentalApplicationFinancialInformationViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=rental_application_financial_information.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_rental_application_financial_information_delete(
    api_rf, rental_application_financial_information_factory, user_with_permissions
):
    """
    Testing :py:meth:`lease.views.RentalApplicationFinancialInformationViewSet.delete` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationfinancialinformation")])
    rental_application_financial_information = rental_application_financial_information_factory(
        subscription=user.associated_subscription
    )

    with assertNumQueries(4):
        url = reverse(
            "lease:rental-application-financial-information-detail",
            kwargs={"pk": rental_application_financial_information.id},
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = RentalApplicationFinancialInformationViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=rental_application_financial_information.id)

    assert response.status_code == 204

    assert RentalApplicationFinancialInformation.objects.count() == 0
