import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from lease.models import RentalApplicationDependent
from lease.views import RentalApplicationDependentViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"rental_application": 0}, [0], 4),
    ),
)
@pytest.mark.django_db
def test_rental_application_dependent_list(
    api_rf,
    user_with_permissions,
    rental_application_dependent_factory,
    query_params,
    index_result,
    num_queries,
    rental_application_factory,
):
    """
    Testing :py:meth:`lease.views.RentalApplicationDependentViewSet.list` method.
    """
    user = user_with_permissions([("lease", "rentalapplicationdependent")])
    rental_application = rental_application_factory()
    rental_applications = [rental_application.id]
    if "rental_application" in query_params:
        query_params["rental_application"] = rental_applications[query_params["rental_application"]]

    instance_1 = rental_application_dependent_factory(
        rental_application=rental_application, subscription=user.associated_subscription
    )
    instance_2 = rental_application_dependent_factory(subscription=user.associated_subscription)
    instance_3 = rental_application_dependent_factory(subscription=user.associated_subscription)
    rental_application_dependent_factory()

    rental_application_dependents = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("lease:rental-application-dependent-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = RentalApplicationDependentViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [rental_application_dependents[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "first_name": ["This field is required."],
                "last_name": ["This field is required."],
                "birthday": ["This field is required."],
                "relationship": ["This field is required."],
                "rental_application": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "first_name": "John",
                "last_name": "Doe",
                "birthday": "2021-01-01",
                "relationship": "Test Relationship",
            },
            None,
            201,
            4,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_rental_application_dependent_create(
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
    Testing :py:meth:`lease.views.RentalApplicationDependentViewSet.create` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationdependent")])
    rental_application = rental_application_factory(subscription=user.associated_subscription)
    if status_code == 201:
        data["rental_application"] = rental_application.id

    with assertNumQueries(num_queries):
        url = reverse("lease:rental-application-dependent-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = RentalApplicationDependentViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert RentalApplicationDependent.objects.count() == obj_count


@pytest.mark.django_db
def test_rental_application_dependent_retrieve(api_rf, rental_application_dependent_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.RentalApplicationDependentViewSet.retrieve` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationdependent")])
    rental_application_dependent = rental_application_dependent_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse(
            "lease:rental-application-dependent-detail",
            kwargs={"pk": rental_application_dependent.id},
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = RentalApplicationDependentViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=rental_application_dependent.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "first_name",
        "last_name",
        "birthday",
        "relationship",
        "rental_application",
    }


@pytest.mark.django_db
def test_rental_application_dependent_update(api_rf, rental_application_dependent_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.RentalApplicationDependentViewSet.partial_update` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationdependent")])
    rental_application_dependent = rental_application_dependent_factory(subscription=user.associated_subscription)
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "birthday": "2021-01-01",
        "relationship": "Test Relationship",
        "rental_application": rental_application_dependent.rental_application.id,
    }

    with assertNumQueries(5):
        url = reverse(
            "lease:rental-application-dependent-detail",
            kwargs={"pk": rental_application_dependent.id},
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = RentalApplicationDependentViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=rental_application_dependent.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_rental_application_dependent_delete(api_rf, rental_application_dependent_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.RentalApplicationDependentViewSet.delete` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationdependent")])
    rental_application_dependent = rental_application_dependent_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse(
            "lease:rental-application-dependent-detail",
            kwargs={"pk": rental_application_dependent.id},
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = RentalApplicationDependentViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=rental_application_dependent.id)

    assert response.status_code == 204

    assert RentalApplicationDependent.objects.count() == 0
