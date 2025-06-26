import pytest

from core.models import BaseAttachment

from ..models import (
    Owner,
    OwnerUpcomingActivity,
    Tenant,
    TenantAttachment,
    TenantUpcomingActivity,
    Vendor,
    VendorAddress,
    VendorAttachment,
    VendorType,
)


@pytest.mark.django_db
def test_tenant(tenant_factory, applicant_factory, rental_application_factory, lease_factory):
    """
    Testing :py:class:`people.models.Tenant` model with factory
    """

    applicant = applicant_factory(
        first_name="Jennifer",
        last_name="Tiffany",
        email="avilakevin@example.net",
        phone_number="+15706235644",
    )
    rent_application = rental_application_factory(applicant=applicant)
    lease = lease_factory(rental_application=rent_application)
    tenant = Tenant.objects.get()

    assert Tenant.objects.count() == 1
    assert tenant.first_name == "Jennifer"
    assert tenant.last_name == "Tiffany"
    assert tenant.email == "avilakevin@example.net"
    assert tenant.phone_number == "+15706235644"
    assert tenant.lease == lease
    assert str(tenant) == "Jennifer Tiffany"


@pytest.mark.django_db
def test_tenant_upcoming_activity(tenant_upcoming_activity_factory, tenant_factory, label_factory, user_factory):
    """
    Testing :py:class:`people.models.TenantUpcomingActivity` model with factory
    """

    tenant = tenant_factory()
    label = label_factory()
    assign_to = user_factory()
    upcoming_activity = tenant_upcoming_activity_factory(
        title="Task",
        description="Mention put eat on son standard dream.",
        date="2023-12-12",
        start_time="17:23:51.297908",
        end_time="18:23:51.297908",
        label=label,
        assign_to=assign_to,
        tenant=tenant,
    )

    assert TenantUpcomingActivity.objects.count() == 1
    assert upcoming_activity.title == "Task"
    assert upcoming_activity.description == "Mention put eat on son standard dream."
    assert upcoming_activity.date == "2023-12-12"
    assert upcoming_activity.start_time == "17:23:51.297908"
    assert upcoming_activity.end_time == "18:23:51.297908"
    assert upcoming_activity.label == label
    assert upcoming_activity.assign_to == assign_to
    assert upcoming_activity.tenant == tenant
    assert str(upcoming_activity) == "Task"


@pytest.mark.django_db
def test_tenant_attachment(tenant_attachment_factory, tenant_factory):
    """
    Testing :py:class:`people.models.TenantAttachment` model with factory
    """
    tenant = tenant_factory()
    tenant_attachment = tenant_attachment_factory(
        name="Property Agreement", file="test.pdf", file_type="pdf", tenant=tenant
    )

    tenant_attachments = TenantAttachment.objects.all()
    assert tenant_attachments.count() == 1
    assert tenant_attachment.name == "Property Agreement"
    assert tenant_attachment.file == "test.pdf"
    assert tenant_attachment.file_type == "pdf"
    assert tenant_attachment.tenant == tenant
    assert str(tenant_attachment) == "Property Agreement"
    assert isinstance(tenant_attachment, BaseAttachment)


@pytest.mark.django_db
def test_vendor_type(vendor_type_factory):
    """
    Testing :py:class:`people.models.VendorType` model with factory
    """

    vendor_type = vendor_type_factory(name="Building", description="Himself line positive three safe feel whether.")

    assert VendorType.objects.count() == 1
    assert vendor_type.name == "Building"
    assert vendor_type.description == "Himself line positive three safe feel whether."
    assert str(vendor_type) == "Building"


@pytest.mark.django_db
def test_vendor(vendor_type_factory, vendor_factory):
    """
    Testing :py:class:`people.models.Vendor` model with factory
    """

    vendor_type = vendor_type_factory()
    vendor = vendor_factory(
        first_name="Cynthia",
        last_name="Antonio",
        company_name="Mercer-Dawson",
        use_company_name_as_display_name=True,
        vendor_type=vendor_type,
        gl_account="123456789",
        personal_contact_numbers=["+15706235644"],
        business_contact_numbers=["+15706235644"],
        personal_emails=["tleonard@example.org"],
        business_emails=["tleonard@example.org"],
        website="https://example.com",
        insurance_provide_name="Watts ltd",
        insurance_policy_number="998",
        insurance_expiry_date="2023-12-12",
        tax_identity_type="SSN",
        tax_payer_id="1234",
    )

    assert Vendor.objects.count() == 1
    assert vendor.first_name == "Cynthia"
    assert vendor.last_name == "Antonio"
    assert vendor.company_name == "Mercer-Dawson"
    assert vendor.use_company_name_as_display_name
    assert vendor.vendor_type == vendor_type
    assert vendor.gl_account == "123456789"
    assert vendor.personal_contact_numbers == ["+15706235644"]
    assert vendor.business_contact_numbers == ["+15706235644"]
    assert vendor.personal_emails == ["tleonard@example.org"]
    assert vendor.business_emails == ["tleonard@example.org"]
    assert vendor.website == "https://example.com"
    assert vendor.insurance_provide_name == "Watts ltd"
    assert vendor.insurance_policy_number == "998"
    assert vendor.insurance_expiry_date == "2023-12-12"
    assert vendor.tax_identity_type == "SSN"
    assert vendor.tax_payer_id == "1234"
    assert str(vendor) == "Cynthia Antonio"


@pytest.mark.django_db
def test_vendor_address(vendor_address_factory, vendor_factory):
    """
    Testing :py:class:`people.models.VendorAddress` model with factory
    """

    vendor = vendor_factory()
    vendor_address = vendor_address_factory(
        street_address="0008 Faith Parks Apt. 966",
        city="Berlin",
        state="Brandenburg",
        country="Germany",
        zip="10015",
        vendor=vendor,
    )

    assert VendorAddress.objects.count() == 1
    assert vendor_address.street_address == "0008 Faith Parks Apt. 966"
    assert vendor_address.city == "Berlin"
    assert vendor_address.state == "Brandenburg"
    assert vendor_address.zip == "10015"
    assert vendor_address.country == "Germany"
    assert vendor_address.vendor == vendor
    assert str(vendor_address) == "0008 Faith Parks Apt. 966"


@pytest.mark.django_db
def test_vendor_attachment(vendor_attachment_factory, vendor_factory):
    """
    Testing :py:class:`people.models.VendorAttachment` model with factory
    """
    vendor = vendor_factory()
    vendor_attachment = vendor_attachment_factory(
        name="Property Agreement", file="test.pdf", file_type="pdf", vendor=vendor
    )

    assert VendorAttachment.objects.all().count() == 1
    assert vendor_attachment.name == "Property Agreement"
    assert vendor_attachment.file == "test.pdf"
    assert vendor_attachment.file_type == "pdf"
    assert vendor_attachment.vendor == vendor
    assert str(vendor_attachment) == "Property Agreement"
    assert isinstance(vendor_attachment, BaseAttachment)


@pytest.mark.django_db
def test_owner(owner_people_factory):
    """
    Testing :py:class:`people.models.Owner` model with factory
    """

    owner = owner_people_factory(
        first_name="Cynthia",
        last_name="Antonio",
        company_name="Mercer-Dawson",
        personal_contact_numbers=["+15706235644"],
        company_contact_numbers=["+15706235644"],
        personal_emails=["tleonard@example.org"],
        company_emails=["tleonard@example.org"],
        street_address="0008 Faith Parks Apt. 966",
        city="Berlin",
        state="Brandenburg",
        country="Germany",
        zip="10015",
        tax_payer="Cynthia Antonio",
        tax_payer_id="1234",
        bank_account_title="Cynthia Antonio",
        bank_name="Deutsche Bank",
        bank_branch="Berlin",
        bank_routing_number="12345",
        bank_account_number="1122334455",
        notes="Himself line positive three safe feel whether.",
        is_company_name_as_tax_payer=False,
        is_use_as_display_name=True,
    )

    assert Owner.objects.count() == 1
    assert owner.first_name == "Cynthia"
    assert owner.last_name == "Antonio"
    assert owner.company_name == "Mercer-Dawson"
    assert owner.personal_contact_numbers == ["+15706235644"]
    assert owner.company_contact_numbers == ["+15706235644"]
    assert owner.personal_emails == ["tleonard@example.org"]
    assert owner.company_emails == ["tleonard@example.org"]
    assert owner.street_address == "0008 Faith Parks Apt. 966"
    assert owner.city == "Berlin"
    assert owner.zip == "10015"
    assert owner.country == "Germany"
    assert owner.state == "Brandenburg"
    assert owner.tax_payer == "Cynthia Antonio"
    assert owner.tax_payer_id == "1234"
    assert owner.bank_name == "Deutsche Bank"
    assert owner.bank_branch == "Berlin"
    assert owner.bank_routing_number == "12345"
    assert owner.bank_account_number == "1122334455"
    assert owner.notes == "Himself line positive three safe feel whether."
    assert not owner.is_company_name_as_tax_payer
    assert owner.is_use_as_display_name
    assert str(owner) == "Cynthia Antonio"


@pytest.mark.django_db
def test_owner_upcoming_activity(owner_upcoming_activity_factory, owner_people_factory, label_factory, user_factory):
    """
    Testing :py:class:`people.models.ownerUpcomingActivity` model with factory
    """

    owner = owner_people_factory()
    label = label_factory()
    assign_to = user_factory()
    upcoming_activity = owner_upcoming_activity_factory(
        title="Task",
        description="Mention put eat on son standard dream.",
        date="2023-12-12",
        start_time="17:23:51.297908",
        end_time="18:23:51.297908",
        label=label,
        assign_to=assign_to,
        owner=owner,
    )

    assert OwnerUpcomingActivity.objects.count() == 1
    assert upcoming_activity.title == "Task"
    assert upcoming_activity.description == "Mention put eat on son standard dream."
    assert upcoming_activity.date == "2023-12-12"
    assert upcoming_activity.start_time == "17:23:51.297908"
    assert upcoming_activity.end_time == "18:23:51.297908"
    assert upcoming_activity.label == label
    assert upcoming_activity.assign_to == assign_to
    assert upcoming_activity.owner == owner
    assert str(upcoming_activity) == "Task"
