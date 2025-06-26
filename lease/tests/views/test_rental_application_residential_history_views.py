import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from lease.models import RentalApplicationResidentialHistory
from lease.views import RentalApplicationResidentialHistoryViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"rental_application": 0}, [0], 4),
    ),
)
@pytest.mark.django_db
def test_rental_application_residential_history_list(
    api_rf,
    user_with_permissions,
    rental_application_residential_history_factory,
    query_params,
    index_result,
    num_queries,
    rental_application_factory,
):
    """
    Testing :py:meth:`lease.views.RentalApplicationResidentialHistoryViewSet.list` method.
    """
    user = user_with_permissions([("lease", "rentalapplicationresidentialhistory")])
    rental_application = rental_application_factory()
    rental_applications = [rental_application.id]
    if "rental_application" in query_params:
        query_params["rental_application"] = rental_applications[query_params["rental_application"]]

    instance_1 = rental_application_residential_history_factory(
        rental_application=rental_application, subscription=user.associated_subscription
    )
    instance_2 = rental_application_residential_history_factory(subscription=user.associated_subscription)
    instance_3 = rental_application_residential_history_factory(subscription=user.associated_subscription)
    rental_application_residential_history_factory()
    rental_application_residential_historys = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("lease:rental-application-resident-history-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = RentalApplicationResidentialHistoryViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [rental_application_residential_historys[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "current_address": ["This field is required."],
                "current_country": ["This field is required."],
                "rental_application": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "current_address": "Test Address",
                "current_address_2": "Test Address 2",
                "current_city": "Test City",
                "current_zip_code": "12345",
                "current_country": "Test Country",
                "resident_from": "2021-01-01",
                "resident_to": "2021-01-01",
                "landlord_name": "Test Landlord",
                "landlord_phone_number": "+923111234455",
                "landlord_email": "john@example.com",
                "reason_of_leaving": "Test Reason",
                "monthly_rent": "1000.00",
                "current_state": "Test State",
            },
            None,
            201,
            4,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_rental_application_residential_history_create(
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
    Testing :py:meth:`lease.views.RentalApplicationResidentialHistoryViewSet.create` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationresidentialhistory")])
    rental_application = rental_application_factory()
    if status_code == 201:
        data["rental_application"] = rental_application.id

    with assertNumQueries(num_queries):
        url = reverse("lease:rental-application-resident-history-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = RentalApplicationResidentialHistoryViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert RentalApplicationResidentialHistory.objects.count() == obj_count


@pytest.mark.django_db
def test_rental_application_residential_history_retrieve(
    api_rf, rental_application_residential_history_factory, user_with_permissions
):
    """
    Testing :py:meth:`lease.views.RentalApplicationResidentialHistoryViewSet.retrieve` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationresidentialhistory")])
    rental_application_residential_history = rental_application_residential_history_factory(
        subscription=user.associated_subscription
    )

    with assertNumQueries(3):
        url = reverse(
            "lease:rental-application-resident-history-detail",
            kwargs={"pk": rental_application_residential_history.id},
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = RentalApplicationResidentialHistoryViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=rental_application_residential_history.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "current_address",
        "current_address_2",
        "current_city",
        "current_zip_code",
        "current_country",
        "resident_from",
        "resident_to",
        "landlord_name",
        "landlord_phone_number",
        "landlord_email",
        "reason_of_leaving",
        "rental_application",
        "monthly_rent",
        "current_state",
    }


@pytest.mark.django_db
def test_rental_application_residential_history_update(
    api_rf, rental_application_residential_history_factory, user_with_permissions
):
    """
    Testing :py:meth:`lease.views.RentalApplicationResidentialHistoryViewSet.partial_update` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationresidentialhistory")])
    rental_application_residential_history = rental_application_residential_history_factory(
        subscription=user.associated_subscription
    )
    data = {
        "current_address": "Test Address",
        "current_address_2": "Test Address 2",
        "current_city": "Test City",
        "current_zip_code": "12345",
        "current_country": "Test Country",
        "resident_from": "2021-01-01",
        "resident_to": "2021-01-01",
        "landlord_name": "Test Landlord",
        "landlord_phone_number": "+923111234455",
        "landlord_email": "john@example.com",
        "reason_of_leaving": "Test Reason",
        "rental_application": rental_application_residential_history.rental_application.id,
        "monthly_rent": "1000.00",
        "current_state": "Test State",
    }

    with assertNumQueries(5):
        url = reverse(
            "lease:rental-application-resident-history-detail",
            kwargs={"pk": rental_application_residential_history.id},
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = RentalApplicationResidentialHistoryViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=rental_application_residential_history.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_rental_application_residential_history_delete(
    api_rf, rental_application_residential_history_factory, user_with_permissions
):
    """
    Testing :py:meth:`lease.views.RentalApplicationResidentialHistoryViewSet.delete` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationresidentialhistory")])
    rental_application_residential_history = rental_application_residential_history_factory(
        subscription=user.associated_subscription
    )

    with assertNumQueries(4):
        url = reverse(
            "lease:rental-application-resident-history-detail",
            kwargs={"pk": rental_application_residential_history.id},
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = RentalApplicationResidentialHistoryViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=rental_application_residential_history.id)

    assert response.status_code == 204

    assert RentalApplicationResidentialHistory.objects.count() == 0
