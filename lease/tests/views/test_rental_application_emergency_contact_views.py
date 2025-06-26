import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from lease.models import RentalApplicationEmergencyContact
from lease.views import RentalApplicationEmergencyContactViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"rental_application": 0}, [0], 4),
    ),
)
@pytest.mark.django_db
def test_rental_application_emergency_contact_list(
    api_rf,
    user_with_permissions,
    rental_application_emergency_contact_factory,
    query_params,
    index_result,
    num_queries,
    rental_application_factory,
):
    """
    Testing :py:meth:`lease.views.RentalApplicationEmergencyContactViewSet.list` method.
    """
    user = user_with_permissions([("lease", "rentalapplicationemergencycontact")])
    rental_application = rental_application_factory()
    rental_applications = [rental_application.id]
    if "rental_application" in query_params:
        query_params["rental_application"] = rental_applications[query_params["rental_application"]]

    instance_1 = rental_application_emergency_contact_factory(
        rental_application=rental_application, subscription=user.associated_subscription
    )
    instance_2 = rental_application_emergency_contact_factory(subscription=user.associated_subscription)
    instance_3 = rental_application_emergency_contact_factory(subscription=user.associated_subscription)
    rental_application_emergency_contact_factory()

    rental_application_emergency_contacts = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("lease:rental-application-emergency-contact-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = RentalApplicationEmergencyContactViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [rental_application_emergency_contacts[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "phone_number": ["This field is required."],
                "relationship": ["This field is required."],
                "address": ["This field is required."],
                "rental_application": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "name": "John Doe",
                "phone_number": "+923111234455",
                "relationship": "Test Relationship",
                "address": "Test Address",
            },
            None,
            201,
            4,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_rental_application_emergency_contact_create(
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
    Testing :py:meth:`lease.views.RentalApplicationEmergencyContactViewSet.create` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationemergencycontact")])
    rental_application = rental_application_factory(subscription=user.associated_subscription)
    if status_code == 201:
        data["rental_application"] = rental_application.id

    with assertNumQueries(num_queries):
        url = reverse("lease:rental-application-emergency-contact-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = RentalApplicationEmergencyContactViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert RentalApplicationEmergencyContact.objects.count() == obj_count


@pytest.mark.django_db
def test_rental_application_emergency_contact_retrieve(
    api_rf, rental_application_emergency_contact_factory, user_with_permissions
):
    """
    Testing :py:meth:`lease.views.RentalApplicationEmergencyContactViewSet.retrieve` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationemergencycontact")])
    rental_application_emergency_contact = rental_application_emergency_contact_factory(
        subscription=user.associated_subscription
    )

    with assertNumQueries(3):
        url = reverse(
            "lease:rental-application-emergency-contact-detail", kwargs={"pk": rental_application_emergency_contact.id}
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = RentalApplicationEmergencyContactViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=rental_application_emergency_contact.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "name",
        "phone_number",
        "relationship",
        "address",
        "rental_application",
    }


@pytest.mark.django_db
def test_rental_application_emergency_contact_update(
    api_rf, rental_application_emergency_contact_factory, user_with_permissions
):
    """
    Testing :py:meth:`lease.views.RentalApplicationEmergencyContactViewSet.partial_update` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationemergencycontact")])
    rental_application_emergency_contact = rental_application_emergency_contact_factory(
        subscription=user.associated_subscription
    )
    data = {
        "name": "John Doe",
        "phone_number": "+923111234455",
        "relationship": "Test Relationship",
        "address": "Test Address",
        "rental_application": rental_application_emergency_contact.rental_application.id,
    }

    with assertNumQueries(5):
        url = reverse(
            "lease:rental-application-emergency-contact-detail", kwargs={"pk": rental_application_emergency_contact.id}
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = RentalApplicationEmergencyContactViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=rental_application_emergency_contact.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_rental_application_emergency_contact_delete(
    api_rf, rental_application_emergency_contact_factory, user_with_permissions
):
    """
    Testing :py:meth:`lease.views.RentalApplicationEmergencyContactViewSet.delete` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationemergencycontact")])
    rental_application_emergency_contact = rental_application_emergency_contact_factory(
        subscription=user.associated_subscription
    )

    with assertNumQueries(4):
        url = reverse(
            "lease:rental-application-emergency-contact-detail", kwargs={"pk": rental_application_emergency_contact.id}
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = RentalApplicationEmergencyContactViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=rental_application_emergency_contact.id)

    assert response.status_code == 204

    assert RentalApplicationEmergencyContact.objects.count() == 0
