import random

import factory  # type: ignore[import]
from faker import Faker

from core.tests import BaseAttachmentFactory, SubscriptionAbstractFactory


class RentalApplicationTemplateFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "lease.RentalApplicationTemplate"

    name = factory.Faker("word")
    description = factory.Faker("text")
    general_info = factory.Faker("boolean")
    personal_details = factory.Faker("boolean")
    rental_history = factory.Faker("boolean")
    financial_info = factory.Faker("boolean")
    dependents_info = factory.Faker("boolean")
    other_info = factory.Faker("boolean")


class ApplicantFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "lease.Applicant"

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    phone_number = factory.LazyFunction(lambda: "+1" + Faker().msisdn())
    allow_email_for_rental_application = False
    unit = factory.SubFactory("property.tests.factories.UnitFactory")


class RentalApplicationFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "lease.RentalApplication"
        django_get_or_create = ("applicant",)

    applicant = factory.SubFactory("lease.tests.factories.ApplicantFactory")
    status = "PENDING"
    desired_move_in_date = factory.Faker("date")
    legal_first_name = factory.Faker("first_name")
    legal_last_name = factory.Faker("last_name")
    middle_name = factory.Faker("first_name")
    application_type = "FINANCIALlY_INDEPENDENT"
    phone_number = factory.List([factory.LazyFunction(lambda: "+1" + Faker().msisdn())])
    emails = factory.List([factory.Faker("email")])
    notes = factory.Faker("text")
    birthday = factory.Faker("date")
    ssn_or_tin = factory.Faker("word")
    driving_license_number = str(random.randint(1111, 9999))
    employer_name = factory.Faker("company")
    employer_address = factory.Faker("address")
    employer_address_2 = factory.Faker("address")
    employer_phone_number = factory.LazyFunction(lambda: "+1" + Faker().msisdn())
    employment_city = factory.Faker("city")
    employment_zip_code = factory.Faker("zipcode")
    employment_country = factory.Faker("country")
    monthly_salary = factory.Faker("pydecimal", min_value=0, max_value=1000, right_digits=2)
    position_held = factory.Faker("job")
    years_worked = factory.Faker("random_int")
    supervisor_name = factory.Faker("name")
    supervisor_phone_number = factory.LazyFunction(lambda: "+1" + Faker().msisdn())
    supervisor_email = factory.Faker("email")
    supervisor_title = factory.Faker("job")
    is_defendant_in_any_lawsuit = factory.Faker("boolean")
    is_convicted = factory.Faker("boolean")
    have_filed_case_against_landlord = factory.Faker("boolean")
    is_smoker = factory.Faker("boolean")
    general_info = factory.Faker("boolean")
    personal_details = factory.Faker("boolean")
    rental_history = factory.Faker("boolean")
    financial_info = factory.Faker("boolean")
    dependents_info = factory.Faker("boolean")
    other_info = factory.Faker("boolean")
    is_general_info_filled = factory.Faker("boolean")
    is_personal_details_filled = factory.Faker("boolean")
    is_rental_history_filled = factory.Faker("boolean")
    is_financial_info_filled = factory.Faker("boolean")
    is_dependents_filled = factory.Faker("boolean")
    is_other_info_filled = factory.Faker("boolean")


class RentalApplicationEmergencyContactFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "lease.RentalApplicationEmergencyContact"

    rental_application = factory.SubFactory("lease.tests.factories.RentalApplicationFactory")
    name = factory.Faker("name")
    phone_number = factory.LazyFunction(lambda: "+1" + Faker().msisdn())
    relationship = factory.Faker("word")
    address = factory.Faker("address")


class RentalApplicationResidentialHistoryFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "lease.RentalApplicationResidentialHistory"

    rental_application = factory.SubFactory("lease.tests.factories.RentalApplicationFactory")
    current_address = factory.Faker("address")
    current_address_2 = factory.Faker("address")
    current_city = factory.Faker("city")
    current_zip_code = factory.Faker("zipcode")
    current_country = factory.Faker("country")
    resident_from = factory.Faker("date")
    resident_to = factory.Faker("date")
    landlord_name = factory.Faker("name")
    landlord_phone_number = factory.LazyFunction(lambda: "+1" + Faker().msisdn())
    landlord_email = factory.Faker("email")
    reason_of_leaving = factory.Faker("text")
    monthly_rent = factory.Faker("pydecimal", min_value=0, max_value=1000, right_digits=2)
    current_state = factory.Faker("state")


class RentalApplicationFinancialInformationFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "lease.RentalApplicationFinancialInformation"

    rental_application = factory.SubFactory("lease.tests.factories.RentalApplicationFactory")
    name = factory.Faker("name")
    account_type = factory.Faker("word")
    bank = factory.Faker("company")
    account_number = factory.Faker("word")


class RentalApplicationAdditionalIncomeFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "lease.RentalApplicationAdditionalIncome"

    rental_application = factory.SubFactory("lease.tests.factories.RentalApplicationFactory")
    monthly_income = factory.Faker("pydecimal", min_value=0, max_value=1000, right_digits=2)
    source_of_income = factory.Faker("word")


class RentalApplicationDependentFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "lease.RentalApplicationDependent"

    rental_application = factory.SubFactory("lease.tests.factories.RentalApplicationFactory")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    birthday = factory.Faker("date")
    relationship = factory.Faker("word")


class RentalApplicationPetsFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "lease.RentalApplicationPets"

    rental_application = factory.SubFactory("lease.tests.factories.RentalApplicationFactory")
    name = factory.Faker("name")
    pet_type = factory.Faker("word")
    weight = factory.Faker("pyfloat", min_value=0, max_value=1000, right_digits=2)
    age = factory.Faker("random_int")


class RentalApplicationAttachmentFactory(BaseAttachmentFactory):
    class Meta:
        model = "lease.RentalApplicationAttachment"

    rental_application = factory.SubFactory("lease.tests.factories.RentalApplicationFactory")


class LeaseTemplateFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "lease.LeaseTemplate"

    name = factory.Faker("word")
    description = factory.Faker("text")
    rules_and_policies = factory.List([factory.Faker("text")])
    condition_of_premises = factory.List([factory.Faker("text")])
    right_of_inspection = factory.Faker("boolean")
    conditions_of_moving_out = factory.List([factory.Faker("text")])
    releasing_policies = factory.List([factory.Faker("text")])
    final_statement = factory.Faker("text")


class LeaseFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "lease.Lease"

    rental_application = factory.SubFactory("lease.tests.factories.RentalApplicationFactory")
    lease_type = "FIXED"
    start_date = factory.Faker("date")
    end_date = factory.Faker("date")
    lease_template = factory.SubFactory("lease.tests.factories.LeaseTemplateFactory")
    rent_cycle = "MONTHLY"
    amount = factory.Faker("pydecimal", min_value=0, max_value=1000, right_digits=2)
    gl_account = str(random.randint(1111, 9999))
    description = factory.Faker("text")
    due_date = factory.Faker("date")
    status = "PENDING"
    closed_on = factory.Faker("date")
    unit = factory.SubFactory("property.tests.factories.UnitFactory")
    rules_and_policies = factory.List([factory.Faker("text")])
    condition_of_premises = factory.List([factory.Faker("text")])
    right_of_inspection = factory.Faker("boolean")
    conditions_of_moving_out = factory.List([factory.Faker("text")])
    releasing_policies = factory.List([factory.Faker("text")])
    final_statement = factory.Faker("text")


class SecondaryTenantFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "lease.SecondaryTenant"

    lease = factory.SubFactory("lease.tests.factories.LeaseFactory")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    phone_number = factory.LazyFunction(lambda: "+1" + Faker().msisdn())
    birthday = factory.Faker("date")
    tax_payer_id = factory.Faker("word")
    description = factory.Faker("text")
