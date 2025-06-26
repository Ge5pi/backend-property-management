import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from lease.models import RentalApplication
from lease.views import RentalApplicationViewSet


@pytest.mark.django_db
def test_rental_application_retrieve(api_rf, rental_application_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.RentalApplicationViewSet.retrieve` method.
    """

    user = user_with_permissions([("lease", "rentalapplication")])
    rental_application = rental_application_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse("lease:rental-application-detail", kwargs={"pk": rental_application.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = RentalApplicationViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=rental_application.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "slug",
        "applicant",
        "status",
        "get_status_display",
        "desired_move_in_date",
        "legal_first_name",
        "middle_name",
        "legal_last_name",
        "application_type",
        "get_application_type_display",
        "phone_number",
        "emails",
        "notes",
        "birthday",
        "ssn_or_tin",
        "driving_license_number",
        "employer_name",
        "employer_address",
        "employer_phone_number",
        "employment_city",
        "employment_zip_code",
        "employment_country",
        "monthly_salary",
        "position_held",
        "years_worked",
        "supervisor_name",
        "supervisor_phone_number",
        "supervisor_email",
        "supervisor_title",
        "is_defendant_in_any_lawsuit",
        "is_convicted",
        "have_filed_case_against_landlord",
        "is_smoker",
        "general_info",
        "personal_details",
        "rental_history",
        "financial_info",
        "dependents_info",
        "other_info",
        "is_general_info_filled",
        "is_personal_details_filled",
        "is_rental_history_filled",
        "is_financial_info_filled",
        "is_dependents_filled",
        "is_other_info_filled",
        "lease_id",
    }


@pytest.mark.django_db
def test_rental_application_update(api_rf, rental_application_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.RentalApplicationViewSet.partial_update` method.
    """

    user = user_with_permissions([("lease", "rentalapplication")])
    rental_application = rental_application_factory(subscription=user.associated_subscription)
    data = {
        "status": "DRAFT",
        "desired_move_in_date": "2021-01-01",
        "legal_first_name": "John",
        "middle_name": "Doe",
        "legal_last_name": "Doe",
        "application_type": "FINANCIALlY_INDEPENDENT",
        "phone_number": ["+923111234455"],
        "emails": ["john@example.com"],
        "notes": "Test Notes",
        "birthday": "1990-01-01",
        "ssn_or_tin": "123456789",
        "driving_license_number": "123456789",
        "employer_name": "Test Employer",
        "employer_address": "Test Employer Address",
        "employer_phone_number": "+923111234455",
        "employment_city": "Test City",
        "employment_zip_code": "12345",
        "employment_country": "Test Country",
        "monthly_salary": "1000.00",
        "position_held": "Test Position",
        "years_worked": 5,
        "supervisor_name": "Test Supervisor",
        "supervisor_phone_number": "+923111234455",
        "supervisor_email": "doe@example.com",
        "supervisor_title": "Test Title",
        "is_defendant_in_any_lawsuit": False,
        "is_convicted": False,
        "have_filed_case_against_landlord": False,
        "is_smoker": False,
        "is_general_info_filled": True,
        "is_personal_details_filled": True,
        "is_rental_history_filled": True,
        "is_financial_info_filled": True,
        "is_dependents_filled": True,
        "is_other_info_filled": True,
    }

    with assertNumQueries(5):
        url = reverse("lease:rental-application-detail", kwargs={"pk": rental_application.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = RentalApplicationViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=rental_application.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_rental_application_delete(api_rf, rental_application_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.RentalApplicationViewSet.delete` method.
    """

    user = user_with_permissions([("lease", "rentalapplication")])
    rental_application = rental_application_factory(subscription=user.associated_subscription)

    with assertNumQueries(13):
        url = reverse("lease:rental-application-detail", kwargs={"pk": rental_application.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = RentalApplicationViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=rental_application.id)

    assert response.status_code == 204

    assert RentalApplication.objects.count() == 0
