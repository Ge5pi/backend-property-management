import pytest

from ..models import RentalApplication
from ..serializers import (
    ApplicantSerializer,
    LeaseSerializer,
    LeaseTemplateSerializer,
    RentalApplicationAdditionalIncomeSerializer,
    RentalApplicationAttachmentSerializer,
    RentalApplicationDependentSerializer,
    RentalApplicationEmergencyContactSerializer,
    RentalApplicationFinancialInformationSerializer,
    RentalApplicationPetsSerializer,
    RentalApplicationResidentialHistorySerializer,
    RentalApplicationSerializer,
    RentalApplicationTemplateSerializer,
    SecondaryTenantSerializer,
)


@pytest.mark.django_db
def test_rental_application_template_serializer_read(rental_application_template_factory):
    """
    Testing :py:class:`lease.serializers.RentalApplicationTemplateSerializer` read
    """
    instance = rental_application_template_factory()

    serializer = RentalApplicationTemplateSerializer(instance)

    assert serializer.data == {
        "id": instance.id,
        "name": instance.name,
        "description": instance.description,
        "general_info": instance.general_info,
        "personal_details": instance.personal_details,
        "rental_history": instance.rental_history,
        "financial_info": instance.financial_info,
        "dependents_info": instance.dependents_info,
        "other_info": instance.other_info,
        "created_at": instance.created_at.isoformat().replace("+00:00", "Z"),
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {"name": ["This field is required."]},
            False,
        ),
        (
            {
                "name": "Rental Application Template",
                "description": "Rental Application Template Description",
                "general_info": True,
                "personal_details": True,
                "rental_history": True,
                "financial_info": True,
                "dependents_info": True,
                "other_info": True,
            },
            {
                "name": "Rental Application Template",
                "description": "Rental Application Template Description",
                "general_info": True,
                "personal_details": True,
                "rental_history": True,
                "financial_info": True,
                "dependents_info": True,
                "other_info": True,
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_rental_application_template_serializer_write(data, response, is_valid):
    """
    Testing :py:class:`lease.serializers.RentalApplicationTemplateSerializer` write
    """

    serializer = RentalApplicationTemplateSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_applicant_serializer_read(applicant_factory):
    """
    Testing :py:class:`lease.serializers.ApplicantSerializer` read
    """
    instance = applicant_factory()

    serializer = ApplicantSerializer(instance)

    assert serializer.data == {
        "id": instance.id,
        "first_name": instance.first_name,
        "last_name": instance.last_name,
        "email": instance.email,
        "phone_number": instance.phone_number,
        "allow_email_for_rental_application": instance.allow_email_for_rental_application,
        "unit": instance.unit.id,
        "rental_application": instance.rental_application.id,
        "status_percentage": 0,
        "property_id": instance.unit.parent_property.id,
        "property_name": instance.unit.parent_property.name,
        "unit_name": instance.unit.name,
        "property_rental_application_template": instance.unit.parent_property.rental_application_template.id,
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "first_name": ["This field is required."],
                "last_name": ["This field is required."],
                "email": ["This field is required."],
                "phone_number": ["This field is required."],
                "unit": ["This field is required."],
            },
            False,
        ),
        (
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "phone_number": "+923111234455",
                "allow_email_for_rental_application": True,
            },
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "phone_number": "+923111234455",
                "allow_email_for_rental_application": True,
                "status_percentage": 0,
                "property_name": "Test Property",
                "unit_name": "Test Unit",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_applicant_serializer_write(data, response, is_valid, unit_factory, unit_type_factory, property_factory):
    """
    Testing :py:class:`lease.serializers.ApplicantSerializer` write
    """
    prop = property_factory(name="Test Property")
    unit_type = unit_type_factory(name="Test Unit Type", parent_property=prop)
    unit = unit_factory(name="Test Unit", unit_type=unit_type)
    if is_valid:
        data["unit"] = unit.id
        response["property_id"] = prop.id
        response["unit"] = unit.id
        response["property_rental_application_template"] = prop.rental_application_template.id

    serializer = ApplicantSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_rental_application_serializer_read(rental_application_factory):
    """
    Testing :py:class:`lease.serializers.RentalApplicationSerializer` read
    """
    rental_application_factory()

    instance = RentalApplication.objects.annotate_slug().get()

    serializer = RentalApplicationSerializer(instance)

    assert serializer.data == {
        "id": instance.id,
        "slug": instance.slug,
        "applicant": instance.applicant.id,
        "status": instance.status,
        "get_status_display": instance.get_status_display(),
        "desired_move_in_date": instance.desired_move_in_date,
        "legal_first_name": instance.legal_first_name,
        "middle_name": instance.middle_name,
        "legal_last_name": instance.legal_last_name,
        "application_type": instance.application_type,
        "get_application_type_display": instance.get_application_type_display(),
        "phone_number": instance.phone_number,
        "emails": instance.emails,
        "notes": instance.notes,
        "birthday": instance.birthday,
        "ssn_or_tin": instance.ssn_or_tin,
        "driving_license_number": instance.driving_license_number,
        "employer_name": instance.employer_name,
        "employer_address": instance.employer_address,
        "employer_phone_number": instance.employer_phone_number,
        "employment_city": instance.employment_city,
        "employment_zip_code": instance.employment_zip_code,
        "employment_country": instance.employment_country,
        "monthly_salary": instance.monthly_salary,
        "position_held": instance.position_held,
        "years_worked": instance.years_worked,
        "supervisor_name": instance.supervisor_name,
        "supervisor_phone_number": instance.supervisor_phone_number,
        "supervisor_email": instance.supervisor_email,
        "supervisor_title": instance.supervisor_title,
        "is_defendant_in_any_lawsuit": instance.is_defendant_in_any_lawsuit,
        "is_convicted": instance.is_convicted,
        "have_filed_case_against_landlord": instance.have_filed_case_against_landlord,
        "is_smoker": instance.is_smoker,
        "general_info": instance.general_info,
        "personal_details": instance.personal_details,
        "rental_history": instance.rental_history,
        "financial_info": instance.financial_info,
        "dependents_info": instance.dependents_info,
        "other_info": instance.other_info,
        "is_general_info_filled": instance.is_general_info_filled,
        "is_personal_details_filled": instance.is_personal_details_filled,
        "is_rental_history_filled": instance.is_rental_history_filled,
        "is_financial_info_filled": instance.is_financial_info_filled,
        "is_dependents_filled": instance.is_dependents_filled,
        "is_other_info_filled": instance.is_other_info_filled,
        "lease_id": None,
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {
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
            },
            {
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
                "lease_id": None,
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_rental_application_serializer_write(data, response, is_valid):
    """
    Testing :py:class:`lease.serializers.RentalApplicationSerializer` write
    """

    serializer = RentalApplicationSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_rental_application_emergency_contact_serializer_read(rental_application_emergency_contact_factory):
    """
    Testing :py:class:`lease.serializers.RentalApplicationEmergencyContactSerializer` read
    """
    instance = rental_application_emergency_contact_factory()

    serializer = RentalApplicationEmergencyContactSerializer(instance)

    assert serializer.data == {
        "id": instance.id,
        "name": instance.name,
        "phone_number": instance.phone_number,
        "relationship": instance.relationship,
        "address": instance.address,
        "rental_application": instance.rental_application.id,
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
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
            False,
        ),
        (
            {
                "name": "John Doe",
                "phone_number": "+923111234455",
                "relationship": "Test Relationship",
                "address": "Test Address",
            },
            {
                "name": "John Doe",
                "phone_number": "+923111234455",
                "relationship": "Test Relationship",
                "address": "Test Address",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_rental_application_emergency_contact_serializer_write(data, response, is_valid, rental_application_factory):
    """
    Testing :py:class:`lease.serializers.RentalApplicationEmergencyContactSerializer` write
    """
    rental_application = rental_application_factory()

    if is_valid:
        data["rental_application"] = rental_application.id
        response["rental_application"] = rental_application.id

    serializer = RentalApplicationEmergencyContactSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_rental_application_residential_history_serializer_read(rental_application_residential_history_factory):
    """
    Testing :py:class:`lease.serializers.RentalApplicationResidentialHistorySerializer` read
    """
    instance = rental_application_residential_history_factory()

    serializer = RentalApplicationResidentialHistorySerializer(instance)

    assert serializer.data == {
        "id": instance.id,
        "current_address": instance.current_address,
        "current_address_2": instance.current_address_2,
        "current_city": instance.current_city,
        "current_zip_code": instance.current_zip_code,
        "current_country": instance.current_country,
        "resident_from": instance.resident_from,
        "resident_to": instance.resident_to,
        "landlord_name": instance.landlord_name,
        "landlord_phone_number": instance.landlord_phone_number,
        "landlord_email": instance.landlord_email,
        "reason_of_leaving": instance.reason_of_leaving,
        "rental_application": instance.rental_application.id,
        "monthly_rent": str(instance.monthly_rent),
        "current_state": instance.current_state,
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "current_address": ["This field is required."],
                "current_country": ["This field is required."],
                "rental_application": ["This field is required."],
            },
            False,
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
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_rental_application_residential_history_serializer_write(data, response, is_valid, rental_application_factory):
    """
    Testing :py:class:`lease.serializers.RentalApplicationResidentialHistorySerializer` write
    """
    rental_application = rental_application_factory()

    if is_valid:
        data["rental_application"] = rental_application.id
        response["rental_application"] = rental_application.id

    serializer = RentalApplicationResidentialHistorySerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_rental_application_financial_information_serializer_read(rental_application_financial_information_factory):
    """
    Testing :py:class:`lease.serializers.RentalApplicationFinancialInformationSerializer` read
    """
    instance = rental_application_financial_information_factory()

    serializer = RentalApplicationFinancialInformationSerializer(instance)

    assert serializer.data == {
        "id": instance.id,
        "name": instance.name,
        "account_type": instance.account_type,
        "bank": instance.bank,
        "account_number": instance.account_number,
        "rental_application": instance.rental_application.id,
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
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
            False,
        ),
        (
            {
                "name": "Test Name",
                "account_type": "Test Account Type",
                "bank": "Test Bank",
                "account_number": "123456789",
            },
            {
                "name": "Test Name",
                "account_type": "Test Account Type",
                "bank": "Test Bank",
                "account_number": "123456789",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_rental_application_financial_information_serializer_write(
    data, response, is_valid, rental_application_factory
):
    """
    Testing :py:class:`lease.serializers.RentalApplicationFinancialInformationSerializer` write
    """
    rental_application = rental_application_factory()

    if is_valid:
        data["rental_application"] = rental_application.id
        response["rental_application"] = rental_application.id

    serializer = RentalApplicationFinancialInformationSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_rental_application_additional_income_serializer_read(rental_application_additional_income_factory):
    """
    Testing :py:class:`lease.serializers.RentalApplicationAdditionalIncomeSerializer` read
    """
    instance = rental_application_additional_income_factory()

    serializer = RentalApplicationAdditionalIncomeSerializer(instance)

    assert serializer.data == {
        "id": instance.id,
        "monthly_income": str(instance.monthly_income),
        "source_of_income": instance.source_of_income,
        "rental_application": instance.rental_application.id,
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "monthly_income": ["This field is required."],
                "source_of_income": ["This field is required."],
                "rental_application": ["This field is required."],
            },
            False,
        ),
        (
            {
                "monthly_income": "1000.00",
                "source_of_income": "Test Source",
            },
            {
                "monthly_income": "1000.00",
                "source_of_income": "Test Source",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_rental_application_additional_income_serializer_write(data, response, is_valid, rental_application_factory):
    """
    Testing :py:class:`lease.serializers.RentalApplicationAdditionalIncomeSerializer` write
    """
    rental_application = rental_application_factory()

    if is_valid:
        data["rental_application"] = rental_application.id
        response["rental_application"] = rental_application.id

    serializer = RentalApplicationAdditionalIncomeSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_rental_application_dependent_serializer_read(rental_application_dependent_factory):
    """
    Testing :py:class:`lease.serializers.RentalApplicationDependentSerializer` read
    """
    instance = rental_application_dependent_factory()

    serializer = RentalApplicationDependentSerializer(instance)

    assert serializer.data == {
        "id": instance.id,
        "first_name": instance.first_name,
        "last_name": instance.last_name,
        "birthday": instance.birthday,
        "relationship": instance.relationship,
        "rental_application": instance.rental_application.id,
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
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
            False,
        ),
        (
            {
                "first_name": "John",
                "last_name": "Doe",
                "birthday": "2021-01-01",
                "relationship": "Test Relationship",
            },
            {
                "first_name": "John",
                "last_name": "Doe",
                "birthday": "2021-01-01",
                "relationship": "Test Relationship",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_rental_application_dependent_serializer_write(data, response, is_valid, rental_application_factory):
    """
    Testing :py:class:`lease.serializers.RentalApplicationDependentSerializer` write
    """
    rental_application = rental_application_factory()

    if is_valid:
        data["rental_application"] = rental_application.id
        response["rental_application"] = rental_application.id

    serializer = RentalApplicationDependentSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_rental_application_pets_serializer_read(rental_application_pets_factory):
    """
    Testing :py:class:`lease.serializers.RentalApplicationPetsSerializer` read
    """
    instance = rental_application_pets_factory()

    serializer = RentalApplicationPetsSerializer(instance)

    assert serializer.data == {
        "id": instance.id,
        "name": instance.name,
        "pet_type": instance.pet_type,
        "weight": instance.weight,
        "age": instance.age,
        "rental_application": instance.rental_application.id,
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "pet_type": ["This field is required."],
                "rental_application": ["This field is required."],
            },
            False,
        ),
        (
            {
                "name": "Test Name",
                "pet_type": "Test Type",
                "weight": 100,
                "age": 5,
            },
            {
                "name": "Test Name",
                "pet_type": "Test Type",
                "weight": 100.0,
                "age": 5,
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_rental_application_pets_serializer_write(data, response, is_valid, rental_application_factory):
    """
    Testing :py:class:`lease.serializers.RentalApplicationPetsSerializer` write
    """
    rental_application = rental_application_factory()

    if is_valid:
        data["rental_application"] = rental_application.id
        response["rental_application"] = rental_application.id

    serializer = RentalApplicationPetsSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_rental_application_attachment_serializer_read(rental_application_attachment_factory):
    """
    Testing :py:class:`lease.serializers.RentalApplicationAttachmentSerializer` read
    """
    instance = rental_application_attachment_factory()

    serializer = RentalApplicationAttachmentSerializer(instance)

    assert serializer.data == {
        "id": instance.id,
        "name": instance.name,
        "created_by": None,
        "file": instance.file,
        "rental_application": instance.rental_application.id,
        "file_type": instance.file_type,
        "updated_at": instance.updated_at.isoformat().replace("+00:00", "Z"),
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "file": ["This field is required."],
                "file_type": ["This field is required."],
                "rental_application": ["This field is required."],
            },
            False,
        ),
        (
            {
                "name": "Test Name",
                "file": "Test File",
                "file_type": "image/jpeg",
            },
            {
                "name": "Test Name",
                "file": "Test File",
                "file_type": "image/jpeg",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_rental_application_attachment_serializer_write(data, response, is_valid, rental_application_factory):
    """
    Testing :py:class:`lease.serializers.RentalApplicationAttachmentSerializer` write
    """
    rental_application = rental_application_factory()

    if is_valid:
        data["rental_application"] = rental_application.id
        response["rental_application"] = rental_application.id

    serializer = RentalApplicationAttachmentSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_lease_template_serializer_read(lease_template_factory):
    """
    Testing :py:class:`lease.serializers.LeaseTemplateSerializer` read
    """
    instance = lease_template_factory()

    serializer = LeaseTemplateSerializer(instance)

    assert serializer.data == {
        "id": instance.id,
        "name": instance.name,
        "description": instance.description,
        "rules_and_policies": instance.rules_and_policies,
        "condition_of_premises": instance.condition_of_premises,
        "right_of_inspection": instance.right_of_inspection,
        "conditions_of_moving_out": instance.conditions_of_moving_out,
        "releasing_policies": instance.releasing_policies,
        "final_statement": instance.final_statement,
        "created_at": instance.created_at.isoformat().replace("+00:00", "Z"),
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {"name": ["This field is required."]},
            False,
        ),
        (
            {
                "name": "Test Name",
                "description": "Test Description",
                "rules_and_policies": ["Test Rules"],
                "condition_of_premises": ["Test Conditions"],
                "right_of_inspection": True,
                "conditions_of_moving_out": ["Test Conditions"],
                "releasing_policies": ["Test Policies"],
                "final_statement": "Test Statement",
            },
            {
                "name": "Test Name",
                "description": "Test Description",
                "rules_and_policies": ["Test Rules"],
                "condition_of_premises": ["Test Conditions"],
                "right_of_inspection": True,
                "conditions_of_moving_out": ["Test Conditions"],
                "releasing_policies": ["Test Policies"],
                "final_statement": "Test Statement",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_lease_template_serializer_write(data, response, is_valid):
    """
    Testing :py:class:`lease.serializers.LeaseTemplateSerializer` write
    """
    serializer = LeaseTemplateSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_lease_serializer_read(lease_factory):
    """
    Testing :py:class:`lease.serializers.LeaseSerializer` read
    """
    instance = lease_factory()

    serializer = LeaseSerializer(instance)

    assert serializer.data == {
        "id": instance.id,
        "rental_application": instance.rental_application.id,
        "lease_type": instance.lease_type,
        "get_lease_type_display": instance.get_lease_type_display(),
        "start_date": instance.start_date,
        "end_date": instance.end_date,
        "lease_template": instance.lease_template.id,
        "rent_cycle": instance.rent_cycle,
        "get_rent_cycle_display": instance.get_rent_cycle_display(),
        "amount": str(instance.amount),
        "gl_account": instance.gl_account,
        "description": instance.description,
        "due_date": instance.due_date,
        "status": instance.status,
        "get_status_display": instance.get_status_display(),
        "closed_on": instance.closed_on,
        "unit": instance.unit.id,
        "created_at": instance.created_at.isoformat().replace("+00:00", "Z"),
        "primary_tenant": instance.primary_tenant.id,
        "property_id": instance.unit.parent_property.id,
        "property_name": instance.unit.parent_property.name,
        "unit_name": instance.unit.name,
        "tenant_first_name": instance.primary_tenant.first_name,
        "tenant_last_name": instance.primary_tenant.last_name,
        "owners": [],
        "applicant_id": instance.rental_application.applicant.id,
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "applicant": ["This field is required."],
                "lease_type": ["This field is required."],
                "start_date": ["This field is required."],
                "end_date": ["This field is required."],
                "rent_cycle": ["This field is required."],
                "amount": ["This field is required."],
                "gl_account": ["This field is required."],
                "due_date": ["This field is required."],
            },
            False,
        ),
        (
            {
                "lease_type": "FIXED",
                "get_lease_type_display": "Fixed",
                "start_date": "2001-07-04",
                "end_date": "1985-04-20",
                "rent_cycle": "MONTHLY",
                "get_rent_cycle_display": "Monthly",
                "amount": "118.01",
                "gl_account": "8854",
                "description": "Trouble parent dog billion send add plant decade.",
                "due_date": "1985-07-25",
                "status": "ACTIVE",
                "get_status_display": "PENDING",
                "closed_on": "2010-04-22",
            },
            {
                "lease_type": "FIXED",
                "start_date": "2001-07-04",
                "end_date": "1985-04-20",
                "lease_template": None,
                "rent_cycle": "MONTHLY",
                "amount": "118.01",
                "gl_account": "8854",
                "description": "Trouble parent dog billion send add plant decade.",
                "due_date": "1985-07-25",
                "status": "ACTIVE",
                "closed_on": "2010-04-22",
                "owners": [],
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_lease_serializer_write(data, response, is_valid, applicant_factory):
    """
    Testing :py:class:`lease.serializers.LeaseSerializer` write
    """
    applicant = applicant_factory()

    if is_valid:
        data["applicant"] = applicant.id

    serializer = LeaseSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_secondary_tenant_serializer_read(secondary_tenant_factory):
    """
    Testing :py:class:`lease.serializers.SecondaryTenantSerializer` read
    """
    instance = secondary_tenant_factory()

    serializer = SecondaryTenantSerializer(instance)

    assert serializer.data == {
        "id": instance.id,
        "first_name": instance.first_name,
        "last_name": instance.last_name,
        "email": instance.email,
        "birthday": instance.birthday,
        "phone_number": instance.phone_number,
        "tax_payer_id": instance.tax_payer_id,
        "description": instance.description,
        "lease": instance.lease.id,
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "first_name": ["This field is required."],
                "last_name": ["This field is required."],
                "birthday": ["This field is required."],
                "phone_number": ["This field is required."],
                "tax_payer_id": ["This field is required."],
                "lease": ["This field is required."],
            },
            False,
        ),
        (
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "birthday": "2021-01-01",
                "phone_number": "+923111234455",
                "tax_payer_id": "123456789",
                "description": "Test Description",
                "lease": 1,
            },
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "birthday": "2021-01-01",
                "phone_number": "+923111234455",
                "tax_payer_id": "123456789",
                "description": "Test Description",
                "lease": 1,
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_secondary_tenant_serializer_write(data, response, is_valid, lease_factory):
    """
    Testing :py:class:`lease.serializers.SecondaryTenantSerializer` write
    """
    lease = lease_factory()

    if is_valid:
        data["lease"] = lease.id
        response["lease"] = lease.id

    serializer = SecondaryTenantSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response
