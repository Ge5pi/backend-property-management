import factory  # type: ignore[import]
from faker import Faker

from core.tests import BaseAttachmentFactory, SubscriptionAbstractFactory, UpcomingActivityAbstractFactory


class TenantFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "people.Tenant"
        django_get_or_create = ("lease",)

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    phone_number = factory.LazyFunction(lambda: "+1" + Faker().msisdn())
    lease = factory.SubFactory("lease.tests.factories.LeaseFactory")


class TenantUpcomingActivityFactory(UpcomingActivityAbstractFactory):
    class Meta:
        model = "people.TenantUpcomingActivity"
        abstract = False

    tenant = factory.SubFactory("people.tests.factories.TenantFactory")


class TenantAttachmentFactory(BaseAttachmentFactory):
    class Meta:
        model = "people.TenantAttachment"
        abstract = False

    tenant = factory.SubFactory("people.tests.factories.TenantFactory")


class VendorTypeFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "people.VendorType"

    name = factory.Faker("word")
    description = factory.Faker("text")


class VendorFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "people.Vendor"

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    company_name = factory.Faker("company")
    use_company_name_as_display_name = factory.Faker("boolean")
    vendor_type = factory.SubFactory("people.tests.factories.VendorTypeFactory")
    gl_account = factory.Faker("word")
    personal_contact_numbers = factory.List([factory.LazyFunction(lambda: "+1" + Faker().msisdn())])
    business_contact_numbers = factory.List([factory.LazyFunction(lambda: "+1" + Faker().msisdn())])
    personal_emails = factory.List([factory.Faker("email")])
    business_emails = factory.List([factory.Faker("email")])
    website = factory.Faker("url")
    insurance_provide_name = factory.Faker("company")
    insurance_policy_number = factory.Faker("random_number")
    insurance_expiry_date = factory.Faker("date")
    tax_identity_type = "SSN"
    tax_payer_id = factory.Faker("random_number")


class VendorAddressFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "people.VendorAddress"

    street_address = factory.Faker("street_address")
    city = factory.Faker("city")
    state = factory.Faker("state")
    country = factory.Faker("country")
    zip = factory.Faker("postcode")
    vendor = factory.SubFactory("people.tests.factories.VendorFactory")


class VendorAttachmentFactory(BaseAttachmentFactory):
    class Meta:
        model = "people.VendorAttachment"

    vendor = factory.SubFactory("people.tests.factories.VendorFactory")


class OwnerPeopleFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "people.Owner"

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    company_name = factory.Faker("word")
    personal_contact_numbers = factory.List([factory.LazyFunction(lambda: "+1" + Faker().msisdn())])
    company_contact_numbers = factory.List([factory.LazyFunction(lambda: "+1" + Faker().msisdn())])
    personal_emails = factory.List([factory.Faker("email")])
    company_emails = factory.List([factory.Faker("email")])
    street_address = factory.Faker("street_address")
    city = factory.Faker("city")
    state = factory.Faker("state")
    country = factory.Faker("country")
    zip = factory.Faker("postcode")
    tax_payer = factory.Faker("first_name")
    tax_payer_id = factory.Faker("pystr")
    bank_account_title = factory.Faker("first_name")
    bank_name = factory.Faker("word")
    bank_branch = factory.Faker("city")
    bank_routing_number = str(factory.Faker("pyint"))
    bank_account_number = str(factory.Faker("pyint"))
    notes = factory.Faker("text")
    is_company_name_as_tax_payer = factory.Faker("boolean")
    is_use_as_display_name = factory.Faker("boolean")


class OwnerUpcomingActivityFactory(UpcomingActivityAbstractFactory):
    class Meta:
        model = "people.OwnerUpcomingActivity"
        abstract = False

    owner = factory.SubFactory("people.tests.factories.OwnerPeopleFactory")
