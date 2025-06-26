import datetime
from decimal import Decimal

import pytest

from core.models import BaseAttachment, CommonInfoAbstractModel, UpcomingActivityAbstract
from property.models import (
    Property,
    PropertyAttachment,
    PropertyLateFeePolicy,
    PropertyLeaseRenewalAttachment,
    PropertyLeaseTemplateAttachment,
    PropertyOwner,
    PropertyPhoto,
    PropertyUpcomingActivity,
    PropertyUtilityBilling,
)


@pytest.mark.django_db
def test_property(
    property_factory, property_type_factory, lease_template_factory, rental_application_template_factory
):
    """
    Testing :py:class:`property.models.Property` model with factory
    """
    prop_type = property_type_factory(name="John Property Type")
    lease_template = lease_template_factory(name="John Lease Template")
    rental_application_template = rental_application_template_factory(name="John Rental Application Template")
    prop = property_factory(
        name="John Property",
        address="1234 Main St",
        property_type=prop_type,
        is_cat_allowed=True,
        is_dog_allowed=True,
        is_smoking_allowed=True,
        additional_fees_gl_account="1234",
        additional_fees_percentage=10,
        addition_fees_suppress=False,
        lease_fees_amount=Decimal("100.00"),
        lease_fees_percentage=10,
        lease_fees_commission_type="percentage",
        tax_authority="John Tax Authority",
        portfolio="John Portfolio",
        description="Hold low little upon ago enter. Could day only series.",
        renters_tax_location_code="1234",
        property_owner_license="1234",
        year_built=2020,
        management_start_date=datetime.date(2020, 1, 1),
        management_end_date=datetime.date(2020, 12, 31),
        management_end_reason="Sold",
        nsf_fee=Decimal("100.00"),
        management_fees_amount=Decimal("150.00"),
        management_fees_percentage=10,
        management_commission_type="percentage",
        notes="Everybody college myself network magazine thank when out. Attorney their get finally design account",
        maintenance_limit_amount=Decimal("10.00"),
        insurance_expiration_date=datetime.date(2022, 12, 31),
        has_home_warranty_coverage=True,
        home_warranty_company="Roberson & Sons",
        home_warranty_expiration_date=datetime.date(2022, 12, 31),
        maintenance_notes="Fly south attorney opportunity president parent clear.",
        default_lease_template=lease_template,
        default_lease_agenda="Everything according hit not through through.",
        default_lease_renewal_template=lease_template,
        default_lease_renewal_agenda="Himself field artist.",
        default_lease_renewal_letter_template="opportunity president parent clear.",
        default_renewal_terms="Smile professional",
        default_renewal_charge_by=Decimal("10.00"),
        default_renewal_additional_fee=Decimal("10.00"),
        rental_application_template=rental_application_template,
    )

    props = Property.objects.all()

    assert props.count() == 1
    assert prop.name == "John Property"
    assert prop.address == "1234 Main St"
    assert prop.property_type == prop_type
    assert prop.is_cat_allowed is True
    assert prop.is_dog_allowed is True
    assert prop.is_smoking_allowed is True
    assert prop.additional_fees_gl_account == "1234"
    assert prop.additional_fees_percentage == 10
    assert prop.addition_fees_suppress is False
    assert prop.lease_fees_amount == Decimal("100.00")
    assert prop.lease_fees_percentage == 10
    assert prop.lease_fees_commission_type == "percentage"
    assert prop.tax_authority == "John Tax Authority"
    assert prop.portfolio == "John Portfolio"
    assert prop.description == "Hold low little upon ago enter. Could day only series."
    assert prop.renters_tax_location_code == "1234"
    assert prop.property_owner_license == "1234"
    assert prop.year_built == 2020
    assert prop.management_start_date == datetime.date(2020, 1, 1)
    assert prop.management_end_date == datetime.date(2020, 12, 31)
    assert prop.management_end_reason == "Sold"
    assert prop.nsf_fee == Decimal("100.00")
    assert prop.management_fees_amount == Decimal("150.00")
    assert prop.management_fees_percentage == 10
    assert prop.management_commission_type == "percentage"
    assert (
        prop.notes
        == "Everybody college myself network magazine thank when out. Attorney their get finally design account"
    )
    assert prop.maintenance_limit_amount == Decimal("10.00")
    assert prop.insurance_expiration_date == datetime.date(2022, 12, 31)
    assert prop.has_home_warranty_coverage is True
    assert prop.home_warranty_company == "Roberson & Sons"
    assert prop.home_warranty_expiration_date == datetime.date(2022, 12, 31)
    assert prop.maintenance_notes == "Fly south attorney opportunity president parent clear."
    assert prop.default_lease_template == lease_template
    assert prop.default_lease_agenda == "Everything according hit not through through."
    assert prop.default_lease_renewal_template == lease_template
    assert prop.default_lease_renewal_agenda == "Himself field artist."
    assert prop.default_lease_renewal_letter_template == "opportunity president parent clear."
    assert prop.default_renewal_terms == "Smile professional"
    assert prop.default_renewal_charge_by == Decimal("10.00")
    assert prop.default_renewal_additional_fee == Decimal("10.00")
    assert prop.rental_application_template == rental_application_template
    assert str(prop) == "John Property"
    assert issubclass(Property, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_property_upcoming_activity(property_upcoming_activity_factory, property_factory, label_factory, user_factory):
    """
    Testing :py:class:`property.models.PropertyUpcomingActivity` model with factory
    """

    parent_property = property_factory()
    label = label_factory()
    assign_to = user_factory()
    upcoming_activity = property_upcoming_activity_factory(
        title="Task",
        description="Mention put eat on son standard dream.",
        date="2023-12-12",
        start_time="17:23:51.297908",
        end_time="18:23:51.297908",
        label=label,
        assign_to=assign_to,
        parent_property=parent_property,
    )

    assert PropertyUpcomingActivity.objects.count() == 1
    assert upcoming_activity.title == "Task"
    assert upcoming_activity.description == "Mention put eat on son standard dream."
    assert upcoming_activity.date == "2023-12-12"
    assert upcoming_activity.start_time == "17:23:51.297908"
    assert upcoming_activity.end_time == "18:23:51.297908"
    assert upcoming_activity.label == label
    assert upcoming_activity.assign_to == assign_to
    assert upcoming_activity.parent_property == parent_property
    assert str(upcoming_activity) == "Task"
    assert isinstance(upcoming_activity, UpcomingActivityAbstract)


@pytest.mark.django_db
def test_property_attachment(property_attachment_factory, property_factory):
    """
    Testing :py:class:`property.models.PropertyAttachment` model with factory
    """
    parent_property = property_factory()
    property_attachment = property_attachment_factory(
        name="Property Agreement", file="test.pdf", file_type="pdf", parent_property=parent_property
    )

    property_attachments = PropertyAttachment.objects.all()
    assert property_attachments.count() == 1
    assert property_attachment.name == "Property Agreement"
    assert property_attachment.file == "test.pdf"
    assert property_attachment.file_type == "pdf"
    assert property_attachment.parent_property == parent_property
    assert str(property_attachment) == "Property Agreement"
    assert isinstance(property_attachment, BaseAttachment)


@pytest.mark.django_db
def test_property_photo(property_photo_factory, property_factory):
    """
    Testing :py:class:`property.models.PropertyPhoto` model with factory
    """
    parent_property = property_factory()
    property_photo = property_photo_factory(image="test.png", is_cover=False, parent_property=parent_property)

    property_attachments = PropertyPhoto.objects.all()
    assert property_attachments.count() == 1
    assert property_photo.image == "test.png"
    assert property_photo.is_cover is False
    assert property_photo.parent_property == parent_property
    assert str(property_photo) == "test.png"


@pytest.mark.django_db
def test_property_lease_template_attachment(property_lease_template_attachment_factory, property_factory):
    """
    Testing :py:class:`property.models.PropertyLeaseTemplateAttachment` model with factory
    """
    parent_property = property_factory()
    property_attachment = property_lease_template_attachment_factory(
        name="Property Agreement", file="test.pdf", file_type="pdf", parent_property=parent_property
    )

    property_attachments = PropertyLeaseTemplateAttachment.objects.all()
    assert property_attachments.count() == 1
    assert property_attachment.name == "Property Agreement"
    assert property_attachment.file == "test.pdf"
    assert property_attachment.file_type == "pdf"
    assert property_attachment.parent_property == parent_property
    assert str(property_attachment) == "Property Agreement"
    assert isinstance(property_attachment, BaseAttachment)


@pytest.mark.django_db
def test_property_lease_renewal_attachment(property_lease_renewal_attachment_factory, property_factory):
    """
    Testing :py:class:`property.models.PropertyLeaseRenewalAttachment` model with factory
    """
    parent_property = property_factory()
    property_attachment = property_lease_renewal_attachment_factory(
        name="Property Agreement", file="test.pdf", file_type="pdf", parent_property=parent_property
    )

    property_attachments = PropertyLeaseRenewalAttachment.objects.all()
    assert property_attachments.count() == 1
    assert property_attachment.name == "Property Agreement"
    assert property_attachment.file == "test.pdf"
    assert property_attachment.file_type == "pdf"
    assert property_attachment.parent_property == parent_property
    assert str(property_attachment) == "Property Agreement"
    assert isinstance(property_attachment, BaseAttachment)


@pytest.mark.django_db
def test_property_owner(property_owner_factory, property_factory, owner_people_factory):
    """
    Testing :py:class:`property.models.PropertyOwner` model with factory
    """
    parent_property = property_factory()
    owner = owner_people_factory()
    property_owner = property_owner_factory(
        percentage_owned=50,
        parent_property=parent_property,
        payment_type="FLAT",
        contract_expiry=datetime.date.today(),
        reserve_funds=Decimal("100.00"),
        fiscal_year_end="June",
        ownership_start_date=datetime.date(2023, 1, 1),
        owner=owner,
    )

    property_owners = PropertyOwner.objects.all()
    assert property_owners.count() == 1
    assert property_owner.percentage_owned == 50
    assert property_owner.parent_property == parent_property
    assert property_owner.payment_type == "FLAT"
    assert property_owner.contract_expiry == datetime.date.today()
    assert property_owner.reserve_funds == Decimal("100.00")
    assert property_owner.fiscal_year_end == "June"
    assert property_owner.ownership_start_date == datetime.date(2023, 1, 1)
    assert property_owner.owner == owner
    assert str(property_owner) == str(owner)
    assert isinstance(property_owner, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_property_utility_billing(property_utility_billing_factory, property_factory, vendor_factory):
    """
    Testing :py:class:`property.models.PropertyUtilityBilling` model with factory
    """
    parent_property = property_factory()
    vendor = vendor_factory()
    property_utility_billing = property_utility_billing_factory(
        utility="Gas",
        vendor=vendor,
        vendor_bill_gl="1234",
        tenant_charge_gl="4321",
        owner_contribution_percentage=50,
        tenant_contribution_percentage=50,
        parent_property=parent_property,
    )

    property_utility_billings = PropertyUtilityBilling.objects.all()
    assert property_utility_billings.count() == 1
    assert property_utility_billing.utility == "Gas"
    assert property_utility_billing.vendor == vendor
    assert property_utility_billing.vendor_bill_gl == "1234"
    assert property_utility_billing.tenant_charge_gl == "4321"
    assert property_utility_billing.owner_contribution_percentage == 50
    assert property_utility_billing.tenant_contribution_percentage == 50
    assert property_utility_billing.parent_property == parent_property
    assert str(property_utility_billing) == "Gas"
    assert isinstance(property_utility_billing, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_property_late_fee_policy(property_factory):
    """
    Testing :py:class:`property.models.PropertyLateFeePolicy` model with factory
    """
    parent_property = property_factory()
    parent_property.late_fee_policy.start_date = datetime.date(2020, 1, 1)
    parent_property.late_fee_policy.end_date = datetime.date(2023, 1, 1)
    parent_property.late_fee_policy.late_fee_type = "flat"
    parent_property.late_fee_policy.base_amount_fee = Decimal("100.00")
    parent_property.late_fee_policy.eligible_charges = "every_charge"
    parent_property.late_fee_policy.charge_daily_late_fees = True
    parent_property.late_fee_policy.daily_amount_per_month_max = Decimal("50.00")
    parent_property.late_fee_policy.grace_period_type = "number_of_days"
    parent_property.late_fee_policy.grace_period = 9
    parent_property.late_fee_policy.parent_property = parent_property
    parent_property.late_fee_policy.save()

    property_late_fee_policies = PropertyLateFeePolicy.objects.all()
    assert property_late_fee_policies.count() == 1
    assert parent_property.late_fee_policy.start_date == datetime.date(2020, 1, 1)
    assert parent_property.late_fee_policy.end_date == datetime.date(2023, 1, 1)
    assert parent_property.late_fee_policy.late_fee_type == "flat"
    assert parent_property.late_fee_policy.base_amount_fee == Decimal("100.00")
    assert parent_property.late_fee_policy.eligible_charges == "every_charge"
    assert parent_property.late_fee_policy.charge_daily_late_fees is True
    assert parent_property.late_fee_policy.daily_amount_per_month_max == Decimal("50.00")
    assert parent_property.late_fee_policy.grace_period_type == "number_of_days"
    assert parent_property.late_fee_policy.grace_period == 9
    assert parent_property.late_fee_policy.parent_property == parent_property
    assert str(parent_property.late_fee_policy) == parent_property.name
    assert isinstance(parent_property.late_fee_policy, CommonInfoAbstractModel)
