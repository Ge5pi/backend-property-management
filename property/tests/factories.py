import datetime
import random

import factory  # type: ignore[import]

from core.tests import BaseAttachmentFactory, SubscriptionAbstractFactory, UpcomingActivityAbstractFactory


class PropertyFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "property.Property"

    name = factory.LazyFunction(lambda: f"{factory.Faker('street_name')} {factory.Faker('building_number')}")
    property_type = factory.SubFactory("system_preferences.tests.factories.PropertyTypeFactory")
    address = factory.Faker("address")
    is_cat_allowed = False
    is_dog_allowed = False
    is_smoking_allowed = False
    additional_fees_gl_account = factory.Faker("random_int", min=1, max=100)
    additional_fees_percentage = factory.Faker("random_int", min=1, max=100)
    addition_fees_suppress = False
    lease_fees_amount = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    lease_fees_percentage = factory.Faker("random_int", min=1, max=100)
    lease_fees_commission_type = "fixed"
    tax_authority = factory.Faker("text", max_nb_chars=30)
    portfolio = factory.Faker("text", max_nb_chars=30)
    description = factory.Faker("text", max_nb_chars=100)
    renters_tax_location_code = factory.Faker("text", max_nb_chars=30)
    property_owner_license = factory.Faker("text", max_nb_chars=30)
    year_built = factory.Faker("random_int", min=1, max=100)
    management_start_date = factory.Faker("date")
    management_end_date = factory.Faker("date")
    management_end_reason = factory.Faker("text", max_nb_chars=30)
    nsf_fee = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    management_fees_amount = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    management_fees_percentage = factory.Faker("random_int", min=1, max=100)
    management_commission_type = "fixed"
    notes = factory.Faker("text", max_nb_chars=100)
    maintenance_limit_amount = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    insurance_expiration_date = factory.Faker("date")
    has_home_warranty_coverage = False
    home_warranty_company = factory.Faker("company")
    home_warranty_expiration_date = factory.Faker("date")
    maintenance_notes = factory.Faker("text", max_nb_chars=100)
    default_lease_template = factory.SubFactory("lease.tests.factories.LeaseTemplateFactory")
    default_lease_agenda = factory.Faker("text", max_nb_chars=100)
    default_lease_renewal_template = factory.SubFactory("lease.tests.factories.LeaseTemplateFactory")
    default_lease_renewal_agenda = factory.Faker("text", max_nb_chars=100)
    default_renewal_terms = "monthly"
    default_renewal_charge_by = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    default_renewal_additional_fee = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    rental_application_template = factory.SubFactory("lease.tests.factories.RentalApplicationTemplateFactory")


class PropertyUtilityBillingFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "property.PropertyUtilityBilling"

    utility = factory.Faker("text", max_nb_chars=30)
    vendor = factory.SubFactory("people.tests.factories.VendorFactory")
    vendor_bill_gl = factory.Faker("random_int", min=1, max=100)
    tenant_charge_gl = factory.Faker("random_int", min=1, max=100)
    owner_contribution_percentage = factory.Faker("random_int", min=1, max=100)
    tenant_contribution_percentage = factory.Faker("random_int", min=1, max=100)
    parent_property = factory.SubFactory("property.tests.factories.PropertyFactory")


class PropertyLateFeePolicyFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "property.PropertyLateFeePolicy"

    start_date = factory.Faker("date")
    end_date = factory.Faker("date")
    late_fee_type = "flat"
    base_amount_fee = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    eligible_charges = factory.Faker("random_int", min=1, max=100)
    charge_daily_late_fees = False
    daily_amount_per_month_max = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    grace_period_type = "number_of_days"
    grace_period = factory.Faker("random_int", min=1, max=100)
    parent_property = factory.SubFactory("property.tests.factories.PropertyFactory")


class PropertyAttachmentFactory(BaseAttachmentFactory):
    class Meta:
        model = "property.PropertyAttachment"
        abstract = False

    parent_property = factory.SubFactory("property.tests.factories.PropertyFactory")


class PropertyLeaseTemplateAttachmentFactory(BaseAttachmentFactory):
    class Meta:
        model = "property.PropertyLeaseTemplateAttachment"
        abstract = False

    parent_property = factory.SubFactory("property.tests.factories.PropertyFactory")


class PropertyLeaseRenewalAttachmentFactory(BaseAttachmentFactory):
    class Meta:
        model = "property.PropertyLeaseRenewalAttachment"
        abstract = False

    parent_property = factory.SubFactory("property.tests.factories.PropertyFactory")


class PropertyPhotoFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "property.PropertyPhoto"

    image = factory.Faker("file_name")
    is_cover = False
    parent_property = factory.SubFactory("property.tests.factories.PropertyFactory")


class PropertyUpcomingActivityFactory(UpcomingActivityAbstractFactory):
    class Meta:
        model = "property.PropertyUpcomingActivity"
        abstract = False

    parent_property = factory.SubFactory("property.tests.factories.PropertyFactory")


class PropertyOwnerFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "property.PropertyOwner"

    percentage_owned = random.randint(1, 100)
    parent_property = factory.SubFactory("property.tests.factories.PropertyFactory")
    payment_type = "FLAT"
    contract_expiry = datetime.date.today()
    reserve_funds = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    fiscal_year_end = "June"
    ownership_start_date = datetime.date(2023, 1, 1)
    owner = factory.SubFactory("people.tests.factories.OwnerPeopleFactory")


class UnitTypeFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "property.UnitType"

    name = factory.Faker("text", max_nb_chars=30)
    parent_property = factory.SubFactory("property.tests.factories.PropertyFactory")

    bed_rooms = factory.Faker("random_int", min=1, max=100)
    bath_rooms = factory.Faker("random_int", min=1, max=100)
    square_feet = factory.Faker("random_int", min=1, max=100)
    market_rent = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    future_market_rent = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    effective_date = factory.Faker("date")
    application_fee = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    estimate_turn_over_cost = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    is_cat_allowed = factory.Faker("boolean")
    is_dog_allowed = factory.Faker("boolean")
    is_smoking_allowed = factory.Faker("boolean")
    marketing_title = factory.Faker("text", max_nb_chars=30)
    marketing_description = factory.Faker("text", max_nb_chars=100)
    marketing_youtube_url = factory.Faker("url")

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        for tag in extracted:
            self.tags.add(tag)


class UnitTypePhotoFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "property.UnitTypePhoto"

    image = factory.Faker("file_name")
    is_cover = False
    unit_type = factory.SubFactory("property.tests.factories.UnitTypeFactory")


class UnitFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "property.Unit"

    name = factory.Faker("text", max_nb_chars=30)
    unit_type = factory.SubFactory("property.tests.factories.UnitTypeFactory")
    market_rent = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    future_market_rent = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    effective_date = factory.Faker("date")
    application_fee = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    estimate_turn_over_cost = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)

    address = factory.Faker("address")
    ready_for_show_on = factory.Faker("date")
    virtual_showing_available = factory.Faker("boolean")
    utility_bills = factory.Faker("boolean")
    utility_bills_date = factory.Faker("date")
    lock_box = factory.Faker("text", max_nb_chars=30)
    description = factory.Faker("text", max_nb_chars=100)
    non_revenues_status = factory.Faker("boolean")

    balance = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    total_charges = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    total_credit = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    due_amount = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    total_payable = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        for tag in extracted:
            self.tags.add(tag)


class UnitUpcomingActivityFactory(UpcomingActivityAbstractFactory):
    class Meta:
        model = "property.UnitUpcomingActivity"
        abstract = False

    unit = factory.SubFactory("property.tests.factories.UnitFactory")


class UnitPhotoFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "property.UnitPhoto"

    image = factory.Faker("file_name")
    is_cover = False
    unit = factory.SubFactory("property.tests.factories.UnitFactory")


class RentableItemFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "property.RentableItem"

    name = factory.Faker("text", max_nb_chars=30)
    description = factory.Faker("text", max_nb_chars=100)
    amount = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    gl_account = factory.Faker("text", max_nb_chars=30)
    tenant = factory.SubFactory("people.tests.factories.TenantFactory")
    status = factory.Faker("boolean")
    parent_property = factory.SubFactory("property.tests.factories.PropertyFactory")
