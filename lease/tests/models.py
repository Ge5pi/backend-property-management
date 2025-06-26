from datetime import date

import pytest

from core.models import BaseAttachment, CommonInfoAbstractModel

from ..models import (
    Applicant,
    Lease,
    LeaseTemplate,
    RentalApplication,
    RentalApplicationAdditionalIncome,
    RentalApplicationAttachment,
    RentalApplicationDependent,
    RentalApplicationEmergencyContact,
    RentalApplicationFinancialInformation,
    RentalApplicationPets,
    RentalApplicationResidentialHistory,
    RentalApplicationTemplate,
    SecondaryTenant,
)


@pytest.mark.django_db
def test_rental_application_template(rental_application_template_factory):
    """
    Testing :py:class:`lease.models.RentalApplicationTemplate` model with factory
    """
    rental_application_template = rental_application_template_factory(
        name="1st Rental Application Template",
        description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        general_info=True,
        personal_details=True,
        rental_history=True,
        financial_info=True,
        dependents_info=True,
        other_info=True,
    )

    rental_application_templates = RentalApplicationTemplate.objects.all()

    assert rental_application_templates.count() == 1
    assert rental_application_template.name == "1st Rental Application Template"
    assert rental_application_template.description == "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    assert rental_application_template.general_info
    assert rental_application_template.personal_details
    assert rental_application_template.rental_history
    assert rental_application_template.financial_info
    assert rental_application_template.dependents_info
    assert rental_application_template.other_info
    assert str(rental_application_template) == "1st Rental Application Template"
    assert issubclass(RentalApplicationTemplate, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_applicant(applicant_factory, unit_factory):
    """
    Testing :py:class:`lease.models.Applicant` model with factory
    """
    unit = unit_factory()

    applicant = applicant_factory(
        first_name="James",
        last_name="Ramirez",
        email="james@example.com",
        allow_email_for_rental_application=True,
        phone_number="+923111234455",
        unit=unit,
    )

    applicants = Applicant.objects.all()

    assert applicants.count() == 1
    assert applicant.first_name == "James"
    assert applicant.last_name == "Ramirez"
    assert applicant.email == "james@example.com"
    assert applicant.allow_email_for_rental_application
    assert applicant.phone_number == "+923111234455"
    assert applicant.unit == unit
    assert str(applicant) == "James Ramirez"
    assert issubclass(Applicant, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_rental_application(applicant_factory):
    """
    Testing :py:class:`lease.models.RentalApplication` model with factory
    """
    applicant = applicant_factory()
    rental_application = applicant.rental_application
    rental_application.status = "DRAFT"
    rental_application.desired_move_in_date = date(2020, 12, 12)
    rental_application.legal_first_name = "James"
    rental_application.legal_last_name = "Ramirez"
    rental_application.middle_name = ""
    rental_application.application_type = "DEPENDENT"
    rental_application.phone_number = ["+923111234455"]
    rental_application.emails = ["john@example.com"]
    rental_application.notes = "Lot truth even still. Great evidence election position box resource."
    rental_application.birthday = date(1990, 12, 12)
    rental_application.ssn_or_tin = "123456789"
    rental_application.driving_license_number = "123456789"
    rental_application.employer_name = "Kathleen Brown"
    rental_application.employer_address = "7267 Martin Loop Apt. 459"
    rental_application.employer_address_2 = "65231 Walsh Ways Suite 50"
    rental_application.employer_phone_number = "+923111234499"
    rental_application.employment_city = "New York"
    rental_application.employment_zip_code = "10001"
    rental_application.employment_country = "USA"
    rental_application.monthly_salary = "1000.00"
    rental_application.position_held = "Software Engineer"
    rental_application.years_worked = "5"
    rental_application.supervisor_name = "Kathleen Brown"
    rental_application.supervisor_phone_number = "+923111234499"
    rental_application.supervisor_email = "brown@example.com"
    rental_application.supervisor_title = "Software Engineer"
    rental_application.is_defendant_in_any_lawsuit = False
    rental_application.is_convicted = False
    rental_application.have_filed_case_against_landlord = False
    rental_application.is_smoker = False
    rental_application.general_info = False
    rental_application.personal_details = False
    rental_application.rental_history = False
    rental_application.financial_info = False
    rental_application.dependents_info = False
    rental_application.other_info = False
    rental_application.is_general_info_filled = False
    rental_application.is_personal_details_filled = False
    rental_application.is_rental_history_filled = False
    rental_application.is_financial_info_filled = False
    rental_application.is_dependents_filled = False
    rental_application.is_other_info_filled = False
    rental_application.save()

    rental_applications = RentalApplication.objects.all()

    assert rental_applications.count() == 1
    assert rental_application.applicant == applicant
    assert rental_application.status == "DRAFT"
    assert rental_application.desired_move_in_date == date(2020, 12, 12)
    assert rental_application.legal_first_name == "James"
    assert rental_application.legal_last_name == "Ramirez"
    assert rental_application.middle_name == ""
    assert rental_application.application_type == "DEPENDENT"
    assert rental_application.phone_number == ["+923111234455"]
    assert rental_application.emails == ["john@example.com"]
    assert rental_application.notes == "Lot truth even still. Great evidence election position box resource."
    assert rental_application.birthday == date(1990, 12, 12)
    assert rental_application.ssn_or_tin == "123456789"
    assert rental_application.driving_license_number == "123456789"
    assert rental_application.employer_name == "Kathleen Brown"
    assert rental_application.employer_address == "7267 Martin Loop Apt. 459"
    assert rental_application.employer_address_2 == "65231 Walsh Ways Suite 50"
    assert rental_application.employer_phone_number == "+923111234499"
    assert rental_application.employment_city == "New York"
    assert rental_application.employment_zip_code == "10001"
    assert rental_application.employment_country == "USA"
    assert rental_application.monthly_salary == "1000.00"
    assert rental_application.position_held == "Software Engineer"
    assert rental_application.years_worked == "5"
    assert rental_application.supervisor_name == "Kathleen Brown"
    assert rental_application.supervisor_phone_number == "+923111234499"
    assert rental_application.supervisor_email == "brown@example.com"
    assert rental_application.supervisor_title == "Software Engineer"
    assert not rental_application.is_defendant_in_any_lawsuit
    assert not rental_application.is_convicted
    assert not rental_application.have_filed_case_against_landlord
    assert not rental_application.is_smoker
    assert not rental_application.general_info
    assert not rental_application.personal_details
    assert not rental_application.rental_history
    assert not rental_application.financial_info
    assert not rental_application.dependents_info
    assert not rental_application.other_info
    assert not rental_application.is_general_info_filled
    assert not rental_application.is_personal_details_filled
    assert not rental_application.is_rental_history_filled
    assert not rental_application.is_financial_info_filled
    assert not rental_application.is_dependents_filled
    assert not rental_application.is_other_info_filled
    assert str(rental_application) == "James Ramirez"
    assert issubclass(RentalApplication, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_rental_application_emergency_contact(
    rental_application_emergency_contact_factory, rental_application_factory
):
    """
    Testing :py:class:`lease.models.RentalApplicationEmergencyContact` model with factory
    """
    rental_application = rental_application_factory()
    rental_application_emergency_contact = rental_application_emergency_contact_factory(
        rental_application=rental_application,
        name="James Ramirez",
        phone_number="+923111234455",
        relationship="Father",
        address="7267 Martin Loop Apt. 459",
    )

    rental_application_emergency_contacts = RentalApplicationEmergencyContact.objects.all()

    assert rental_application_emergency_contacts.count() == 1
    assert rental_application_emergency_contact.rental_application == rental_application
    assert rental_application_emergency_contact.name == "James Ramirez"
    assert rental_application_emergency_contact.phone_number == "+923111234455"
    assert rental_application_emergency_contact.relationship == "Father"
    assert rental_application_emergency_contact.address == "7267 Martin Loop Apt. 459"
    assert str(rental_application_emergency_contact) == "James Ramirez"
    assert issubclass(RentalApplicationEmergencyContact, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_rental_application_residential_history(
    rental_application_residential_history_factory, rental_application_factory
):
    """
    Testing :py:class:`lease.models.RentalApplicationResidentialHistory` model with factory
    """
    rental_application = rental_application_factory()
    rental_application_residential_history = rental_application_residential_history_factory(
        rental_application=rental_application,
        current_address="7267 Martin Loop Apt. 459",
        current_address_2="65231 Walsh Ways Suite 50",
        current_city="New York",
        current_zip_code="10001",
        current_country="USA",
        resident_from=date(2020, 12, 12),
        resident_to=date(2020, 12, 12),
        landlord_name="James Ramirez",
        landlord_phone_number="+923111234455",
        landlord_email="james@example.com",
        reason_of_leaving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        monthly_rent="1000.00",
        current_state="NY",
    )

    rental_application_residential_histories = RentalApplicationResidentialHistory.objects.all()

    assert rental_application_residential_histories.count() == 1
    assert rental_application_residential_history.rental_application == rental_application
    assert rental_application_residential_history.current_address == "7267 Martin Loop Apt. 459"
    assert rental_application_residential_history.current_address_2 == "65231 Walsh Ways Suite 50"
    assert rental_application_residential_history.current_city == "New York"
    assert rental_application_residential_history.current_zip_code == "10001"
    assert rental_application_residential_history.current_country == "USA"
    assert rental_application_residential_history.resident_from == date(2020, 12, 12)
    assert rental_application_residential_history.resident_to == date(2020, 12, 12)
    assert rental_application_residential_history.landlord_name == "James Ramirez"
    assert rental_application_residential_history.landlord_phone_number == "+923111234455"
    assert rental_application_residential_history.landlord_email == "james@example.com"
    assert (
        rental_application_residential_history.reason_of_leaving
        == "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    )
    assert rental_application_residential_history.monthly_rent == "1000.00"
    assert rental_application_residential_history.current_state == "NY"
    assert str(rental_application_residential_history) == "7267 Martin Loop Apt. 459..."
    assert issubclass(RentalApplicationResidentialHistory, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_rental_application_financial_information(
    rental_application_financial_information_factory, rental_application_factory
):
    """
    Testing :py:class:`lease.models.RentalApplicationFinancialInformation` model with factory
    """
    rental_application = rental_application_factory()
    rental_application_financial_information = rental_application_financial_information_factory(
        rental_application=rental_application,
        name="James Ramirez",
        account_type="SAVINGS",
        bank="Bank of America",
        account_number="123456789",
    )

    rental_application_financial_informations = RentalApplicationFinancialInformation.objects.all()

    assert rental_application_financial_informations.count() == 1
    assert rental_application_financial_information.rental_application == rental_application
    assert rental_application_financial_information.name == "James Ramirez"
    assert rental_application_financial_information.account_type == "SAVINGS"
    assert rental_application_financial_information.bank == "Bank of America"
    assert rental_application_financial_information.account_number == "123456789"
    assert str(rental_application_financial_information) == "James Ramirez"
    assert issubclass(RentalApplicationFinancialInformation, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_rental_application_additional_income(
    rental_application_additional_income_factory, rental_application_factory
):
    """
    Testing :py:class:`lease.models.RentalApplicationAdditionalIncome` model with factory
    """
    rental_application = rental_application_factory()
    rental_application_additional_income = rental_application_additional_income_factory(
        rental_application=rental_application,
        monthly_income="1000.00",
        source_of_income="Software Engineer",
    )

    rental_application_additional_incomes = RentalApplicationAdditionalIncome.objects.all()

    assert rental_application_additional_incomes.count() == 1
    assert rental_application_additional_income.rental_application == rental_application
    assert rental_application_additional_income.monthly_income == "1000.00"
    assert rental_application_additional_income.source_of_income == "Software Engineer"
    assert str(rental_application_additional_income) == "Software Engineer"
    assert issubclass(RentalApplicationAdditionalIncome, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_rental_application_dependent(rental_application_dependent_factory, rental_application_factory):
    """
    Testing :py:class:`lease.models.RentalApplicationDependent` model with factory
    """
    rental_application = rental_application_factory()
    rental_application_dependent = rental_application_dependent_factory(
        rental_application=rental_application,
        first_name="James",
        last_name="Ramirez",
        birthday=date(1990, 12, 12),
        relationship="Father",
    )

    rental_application_dependents = RentalApplicationDependent.objects.all()

    assert rental_application_dependents.count() == 1
    assert rental_application_dependent.rental_application == rental_application
    assert rental_application_dependent.first_name == "James"
    assert rental_application_dependent.last_name == "Ramirez"
    assert rental_application_dependent.birthday == date(1990, 12, 12)
    assert rental_application_dependent.relationship == "Father"
    assert str(rental_application_dependent) == "James Ramirez"
    assert issubclass(RentalApplicationDependent, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_rental_application_pets(rental_application_pets_factory, rental_application_factory):
    """
    Testing :py:class:`lease.models.RentalApplicationPets` model with factory
    """
    rental_application = rental_application_factory()
    rental_application_pets = rental_application_pets_factory(
        rental_application=rental_application,
        pet_type="DOG",
        name="Tommy",
        weight=10,
        age=5,
    )

    rental_application_petss = RentalApplicationPets.objects.all()

    assert rental_application_petss.count() == 1
    assert rental_application_pets.rental_application == rental_application
    assert rental_application_pets.pet_type == "DOG"
    assert rental_application_pets.name == "Tommy"
    assert rental_application_pets.weight == 10
    assert rental_application_pets.age == 5
    assert str(rental_application_pets) == "Tommy"
    assert issubclass(RentalApplicationPets, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_rental_application_attachment(rental_application_attachment_factory, rental_application_factory):
    """
    Testing :py:class:`lease.models.RentalApplicationAttachment` model with factory
    """
    rental_application = rental_application_factory()
    rental_application_attachment = rental_application_attachment_factory(
        rental_application=rental_application, name="Property Agreement", file="test.pdf", file_type="pdf"
    )

    rental_application_attachments = RentalApplicationAttachment.objects.all()

    assert rental_application_attachments.count() == 1
    assert rental_application_attachment.rental_application == rental_application
    assert rental_application_attachment.name == "Property Agreement"
    assert rental_application_attachment.file == "test.pdf"
    assert rental_application_attachment.file_type == "pdf"
    assert str(rental_application_attachment) == "Property Agreement"
    assert issubclass(RentalApplicationAttachment, BaseAttachment)


@pytest.mark.django_db
def test_lease_template(lease_template_factory):
    """
    Testing :py:class:`lease.models.LeaseTemplate` model with factory
    """
    lease_template = lease_template_factory(
        name="1st Lease Template",
        description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        rules_and_policies=["Lorem ipsum dolor sit amet, consectetur adipiscing elit."],
        condition_of_premises=["Lorem ipsum dolor sit amet, consectetur adipiscing elit."],
        right_of_inspection=True,
        conditions_of_moving_out=["Lorem ipsum dolor sit amet, consectetur adipiscing elit."],
        releasing_policies=["Lorem ipsum dolor sit amet, consectetur adipiscing elit."],
        final_statement="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    )

    lease_templates = LeaseTemplate.objects.all()

    assert lease_templates.count() == 1
    assert lease_template.name == "1st Lease Template"
    assert lease_template.description == "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    assert lease_template.rules_and_policies == ["Lorem ipsum dolor sit amet, consectetur adipiscing elit."]
    assert lease_template.condition_of_premises == ["Lorem ipsum dolor sit amet, consectetur adipiscing elit."]
    assert lease_template.right_of_inspection
    assert lease_template.conditions_of_moving_out == ["Lorem ipsum dolor sit amet, consectetur adipiscing elit."]
    assert lease_template.releasing_policies == ["Lorem ipsum dolor sit amet, consectetur adipiscing elit."]
    assert lease_template.final_statement == "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    assert str(lease_template) == "1st Lease Template"
    assert issubclass(LeaseTemplate, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_lease(
    lease_factory,
    rental_application_factory,
    lease_template_factory,
    applicant_factory,
    unit_factory,
    unit_type_factory,
    property_factory,
):
    """
    Testing :py:class:`lease.models.Lease` model with factory
    """
    lease_template = lease_template_factory()
    prop = property_factory(default_lease_template=lease_template)
    unit_type = unit_type_factory(parent_property=prop)
    unit = unit_factory(unit_type=unit_type)
    rental_application = rental_application_factory(applicant=applicant_factory(unit=unit))

    lease = lease_factory(
        rental_application=rental_application,
        lease_template=lease_template,
        lease_type="FIXED",
        start_date=date(2020, 12, 12),
        end_date=date(2020, 12, 12),
        rent_cycle="MONTHLY",
        amount="1000.00",
        gl_account="123456789",
        description="rent",
        due_date=date(2020, 12, 12),
        status="ACTIVE",
        closed_on=date(2020, 12, 12),
        unit=rental_application.applicant.unit,
        rules_and_policies=["Lorem ipsum dolor sit amet, consectetur adipiscing elit."],
        condition_of_premises=["Lorem ipsum dolor sit amet, consectetur adipiscing elit."],
        right_of_inspection=True,
        conditions_of_moving_out=["Lorem ipsum dolor sit amet, consectetur adipiscing elit."],
        releasing_policies=["Lorem ipsum dolor sit amet, consectetur adipiscing elit."],
        final_statement="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    )

    leases = Lease.objects.all()

    assert leases.count() == 1
    assert lease.rental_application == rental_application
    assert lease.lease_type == "FIXED"
    assert lease.start_date == date(2020, 12, 12)
    assert lease.end_date == date(2020, 12, 12)
    assert lease.lease_template == lease_template
    assert lease.rent_cycle == "MONTHLY"
    assert lease.amount == "1000.00"
    assert lease.gl_account == "123456789"
    assert lease.description == "rent"
    assert lease.due_date == date(2020, 12, 12)
    assert lease.status == "ACTIVE"
    assert lease.closed_on == date(2020, 12, 12)
    assert lease.unit == rental_application.applicant.unit
    assert lease.rules_and_policies == lease_template.rules_and_policies
    assert lease.condition_of_premises == lease_template.condition_of_premises
    assert lease.right_of_inspection == lease_template.right_of_inspection
    assert lease.conditions_of_moving_out == lease_template.conditions_of_moving_out
    assert lease.releasing_policies == lease_template.releasing_policies
    assert lease.final_statement == lease_template.final_statement
    assert str(lease) == f"{rental_application.applicant}"
    assert issubclass(Lease, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_secondary_tenant(secondary_tenant_factory, lease_factory):
    """
    Testing :py:class:`lease.models.SecondaryTenant` model with factory
    """
    lease = lease_factory()
    secondary_tenant = secondary_tenant_factory(
        lease=lease,
        first_name="James",
        last_name="Ramirez",
        email="james@example.net",
        phone_number="+923111234455",
        tax_payer_id="123456789",
        description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        birthday=date(1990, 12, 12),
    )

    secondary_tenants = SecondaryTenant.objects.all()

    assert secondary_tenants.count() == 1
    assert secondary_tenant.lease == lease
    assert secondary_tenant.first_name == "James"
    assert secondary_tenant.last_name == "Ramirez"
    assert secondary_tenant.email == "james@example.net"
    assert secondary_tenant.phone_number == "+923111234455"
    assert secondary_tenant.birthday == date(1990, 12, 12)
    assert secondary_tenant.tax_payer_id == "123456789"
    assert secondary_tenant.description == "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    assert str(secondary_tenant) == "James Ramirez"
    assert issubclass(SecondaryTenant, CommonInfoAbstractModel)
