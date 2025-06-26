import pytest

from authentication.serializers import UserSerializer

from ..serializers import (
    OwnerPeopleSerializer,
    OwnerUpcomingActivitySerializer,
    TenantAttachmentSerializer,
    TenantSerializer,
    TenantUpcomingActivitySerializer,
    VendorAddressSerializer,
    VendorAttachmentSerializer,
    VendorSerializer,
    VendorTypeSerializer,
)
from .models import Tenant, Vendor, VendorType


@pytest.mark.django_db
def test_tenant_upcoming_activity_serializer_read(tenant_upcoming_activity_factory):
    """
    Testing :py:class:`people.serializers.TenantUpcomingActivitySerializer` read
    """

    instance = tenant_upcoming_activity_factory()

    serializer = TenantUpcomingActivitySerializer(instance)
    assert serializer.data["id"] == instance.id
    assert serializer.data["title"] == instance.title
    assert serializer.data["description"] == instance.description
    assert serializer.data["date"] == instance.date
    assert serializer.data["start_time"] == instance.start_time
    assert serializer.data["end_time"] == instance.end_time
    assert serializer.data["label"] == instance.label.id
    assert serializer.data["assign_to"] == instance.assign_to.id
    assert serializer.data["status"] == instance.status
    assert serializer.data["tenant"] == instance.tenant.id
    assert serializer.data["label_name"] == instance.label.name
    assert serializer.data["assign_to_first_name"] == instance.assign_to.first_name
    assert serializer.data["assign_to_last_name"] == instance.assign_to.last_name
    assert serializer.data["assign_to_username"] == instance.assign_to.username
    assert serializer.data["tenant_first_name"] == instance.tenant.first_name
    assert serializer.data["tenant_last_name"] == instance.tenant.last_name
    assert serializer.data.keys() == {
        "id",
        "title",
        "description",
        "date",
        "start_time",
        "end_time",
        "label",
        "assign_to",
        "status",
        "tenant",
        "label_name",
        "assign_to_first_name",
        "assign_to_last_name",
        "assign_to_username",
        "tenant_first_name",
        "tenant_last_name",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "title": ["This field is required."],
                "date": ["This field is required."],
                "tenant": ["This field is required."],
            },
            False,
        ),
        (
            {
                "title": "lorem ipsum",
                "description": "lorem ipsum dolor",
                "date": "1977-08-31",
                "start_time": "14:23:03",
                "end_time": "14:23:03",
                "label": 1,
                "assign_to": 1,
                "status": False,
                "tenant": 1,
            },
            {
                "title": "lorem ipsum",
                "description": "lorem ipsum dolor",
                "date": "1977-08-31",
                "start_time": "14:23:03",
                "end_time": "14:23:03",
                "label": 1,
                "assign_to": 1,
                "status": False,
                "tenant": 1,
                "label_name": "Extra",
                "assign_to_first_name": "John",
                "assign_to_last_name": "Smith",
                "assign_to_username": "john_smith",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_tenant_upcoming_activity_serializer_write(
    data, response, is_valid, tenant_factory, user_factory, label_factory
):
    """
    Testing :py:class:`people.serializers.TenantUpcomingActivitySerializer` write
    """

    tenant = tenant_factory()
    user = user_factory(first_name="John", last_name="Smith", username="john_smith")
    label = label_factory(name="Extra")

    if is_valid:
        data["tenant"] = tenant.id
        data["assign_to"] = user.id
        data["label"] = label.id
        response["tenant"] = tenant.id
        response["assign_to"] = user.id
        response["label"] = label.id
        response["tenant_first_name"] = tenant.first_name
        response["tenant_last_name"] = tenant.last_name

    serializer = TenantUpcomingActivitySerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_tenant_attachment_serializer_read(tenant_factory, tenant_attachment_factory, user_factory):
    """
    Testing :py:class:`people.serializers.TenantAttachmentSerializer` read
    """
    tenant = tenant_factory()
    user = user_factory()
    instance = tenant_attachment_factory(tenant=tenant, created_by=user)

    serializer = TenantAttachmentSerializer(instance)

    assert serializer.data["tenant"] == tenant.id
    assert serializer.data["created_by"] == UserSerializer(instance.created_by).data
    assert serializer.data["file"] == instance.file
    assert serializer.data["name"] == instance.name
    assert serializer.data["file_type"] == instance.file_type
    assert serializer.data["updated_at"] is not None
    assert serializer.data.keys() == {
        "id",
        "name",
        "created_by",
        "file",
        "tenant",
        "file_type",
        "updated_at",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "file": ["This field is required."],
                "tenant": ["This field is required."],
                "file_type": ["This field is required."],
            },
            False,
        ),
        (
            {
                "tenant": 1,
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            {
                "tenant": 1,
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_tenant_attachment_serializer_write(tenant_factory, data, response, is_valid):
    """
    Testing :py:class:`people.serializers.TenantAttachmentSerializer` write
    """

    tenant = tenant_factory()

    if is_valid:
        data["tenant"] = tenant.id
        response["tenant"] = tenant.id

    serializer = TenantAttachmentSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_tenant_serializer_read(tenant_factory):
    """
    Testing :py:class:`people.serializers.TenantSerializer` read
    """

    tenant_factory()

    instance = Tenant.objects.annotate_status().get()

    serializer = TenantSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["first_name"] == instance.first_name
    assert serializer.data["last_name"] == instance.last_name
    assert serializer.data["email"] == instance.email
    assert serializer.data["phone_number"] == instance.phone_number
    assert serializer.data["status"] == instance.status
    assert serializer.data["property_id"] == instance.lease.unit.parent_property.id
    assert serializer.data["property_name"] == instance.lease.unit.parent_property.name
    assert serializer.data["unit_id"] == instance.lease.unit.id
    assert serializer.data["unit_name"] == instance.lease.unit.name
    assert serializer.data["status"] == instance.status
    assert serializer.data["address"] == instance.lease.unit.parent_property.address
    assert serializer.data["rental_application_id"] == instance.lease.rental_application.id
    assert serializer.data.keys() == {
        "id",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "status",
        "property_name",
        "unit_name",
        "lease",
        "address",
        "property_id",
        "unit_id",
        "rental_application_id",
    }


@pytest.mark.django_db
def test_vendor_type_serializer_read(vendor_type_factory):
    """
    Testing :py:class:`people.serializers.VendorTypeSerializer` read
    """

    vendor_type_factory()

    instance = VendorType.objects.annotate_slug().annotate_vendor_count().get()

    serializer = VendorTypeSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["slug"] == instance.slug
    assert serializer.data["name"] == instance.name
    assert serializer.data["description"] == instance.description
    assert serializer.data["vendor_count"] == instance.vendor_count
    assert serializer.data.keys() == {
        "id",
        "name",
        "slug",
        "description",
        "vendor_count",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "description": ["This field is required."],
            },
            False,
        ),
        (
            {
                "name": "Supplier",
                "description": "lorem ipsum dolor",
            },
            {
                "name": "Supplier",
                "description": "lorem ipsum dolor",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_vendor_type_serializer_write(data, response, is_valid):
    """
    Testing :py:class:`people.serializers.VendorTypeSerializer` write
    """

    serializer = VendorTypeSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_vendor_address_serializer_read(vendor_address_factory):
    """
    Testing :py:class:`people.serializers.VendorAddressSerializer` read
    """

    instance = vendor_address_factory()

    serializer = VendorAddressSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["street_address"] == instance.street_address
    assert serializer.data["city"] == instance.city
    assert serializer.data["state"] == instance.state
    assert serializer.data["zip"] == instance.zip
    assert serializer.data["vendor"] == instance.vendor.id
    assert serializer.data.keys() == {
        "id",
        "street_address",
        "city",
        "state",
        "country",
        "zip",
        "vendor",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "street_address": ["This field is required."],
                "city": ["This field is required."],
                "state": ["This field is required."],
                "country": ["This field is required."],
                "zip": ["This field is required."],
                "vendor": ["This field is required."],
            },
            False,
        ),
        (
            {
                "street_address": "07198 David Plains",
                "city": "New Jennifer",
                "state": "Oregon",
                "country": "Swaziland",
                "zip": "58050",
                "vendor": 1,
            },
            {
                "street_address": "07198 David Plains",
                "city": "New Jennifer",
                "state": "Oregon",
                "country": "Swaziland",
                "zip": "58050",
                "vendor": 1,
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_vendor_address_serializer_write(vendor_factory, data, response, is_valid):
    """
    Testing :py:class:`people.serializers.VendorAddressSerializer` write
    """
    vendor = vendor_factory()

    if is_valid:
        data["vendor"] = vendor.id
        response["vendor"] = vendor.id

    serializer = VendorAddressSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_vendor_attachment_serializer_read(vendor_factory, vendor_attachment_factory, user_factory):
    """
    Testing :py:class:`people.serializers.VendorAttachmentSerializer` read
    """
    vendor = vendor_factory()
    user = user_factory()
    instance = vendor_attachment_factory(vendor=vendor, created_by=user)

    serializer = VendorAttachmentSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["vendor"] == vendor.id
    assert serializer.data["created_by"] == UserSerializer(instance.created_by).data
    assert serializer.data["file"] == instance.file
    assert serializer.data["name"] == instance.name
    assert serializer.data["file_type"] == instance.file_type
    assert serializer.data["updated_at"] is not None
    assert serializer.data.keys() == {
        "id",
        "name",
        "created_by",
        "file",
        "vendor",
        "file_type",
        "updated_at",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "file": ["This field is required."],
                "vendor": ["This field is required."],
                "file_type": ["This field is required."],
            },
            False,
        ),
        (
            {
                "vendor": 1,
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            {
                "vendor": 1,
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_vendor_attachment_serializer_write(vendor_factory, data, response, is_valid):
    """
    Testing :py:class:`people.serializers.VendorAttachmentSerializer` write
    """

    vendor = vendor_factory()

    if is_valid:
        data["vendor"] = vendor.id
        response["vendor"] = vendor.id

    serializer = VendorAttachmentSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_vendor_serializer_read(vendor_factory):
    """
    Testing :py:class:`people.serializers.VendorSerializer` read
    """
    vendor_factory()
    instance = Vendor.objects.annotate_slug().get()

    serializer = VendorSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["first_name"] == instance.first_name
    assert serializer.data["last_name"] == instance.last_name
    assert serializer.data["slug"] == instance.slug
    assert serializer.data["company_name"] == instance.company_name
    assert serializer.data["use_company_name_as_display_name"] == instance.use_company_name_as_display_name
    assert serializer.data["vendor_type"] == instance.vendor_type.id
    assert serializer.data["gl_account"] == instance.gl_account
    assert serializer.data["personal_contact_numbers"] == instance.personal_contact_numbers
    assert serializer.data["business_contact_numbers"] == instance.business_contact_numbers
    assert serializer.data["personal_emails"] == [str(i) for i in instance.personal_emails]
    assert serializer.data["business_emails"] == [str(i) for i in instance.business_emails]
    assert serializer.data["website"] == instance.website
    assert serializer.data["insurance_provide_name"] == instance.insurance_provide_name
    assert serializer.data["insurance_policy_number"] == instance.insurance_policy_number
    assert serializer.data["insurance_expiry_date"] == str(instance.insurance_expiry_date)
    assert serializer.data["tax_identity_type"] == instance.tax_identity_type
    assert serializer.data["get_tax_identity_type_display"] == instance.get_tax_identity_type_display()
    assert serializer.data["tax_payer_id"] == instance.tax_payer_id
    assert serializer.data["vendor_type_name"] == instance.vendor_type.name
    assert serializer.data.keys() == {
        "id",
        "first_name",
        "last_name",
        "slug",
        "company_name",
        "use_company_name_as_display_name",
        "vendor_type",
        "gl_account",
        "personal_contact_numbers",
        "business_contact_numbers",
        "personal_emails",
        "business_emails",
        "website",
        "insurance_provide_name",
        "insurance_policy_number",
        "insurance_expiry_date",
        "tax_identity_type",
        "get_tax_identity_type_display",
        "tax_payer_id",
        "vendor_type_name",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "first_name": ["This field is required."],
                "last_name": ["This field is required."],
                "company_name": ["This field is required."],
                "use_company_name_as_display_name": ["This field is required."],
                "vendor_type": ["This field is required."],
                "gl_account": ["This field is required."],
                "personal_contact_numbers": ["This field is required."],
                "business_contact_numbers": ["This field is required."],
                "personal_emails": ["This field is required."],
                "business_emails": ["This field is required."],
                "website": ["This field is required."],
                "insurance_provide_name": ["This field is required."],
                "insurance_policy_number": ["This field is required."],
                "insurance_expiry_date": ["This field is required."],
                "tax_identity_type": ["This field is required."],
                "tax_payer_id": ["This field is required."],
            },
            False,
        ),
        (
            {
                "first_name": "Steven",
                "last_name": "Ward",
                "company_name": "Lane-Becker",
                "use_company_name_as_display_name": True,
                "vendor_type": 1,
                "gl_account": "16392591156",
                "personal_contact_numbers": ["+923111234455"],
                "business_contact_numbers": ["+923111234455"],
                "personal_emails": ["michelewilson@example.net"],
                "business_emails": ["ahayes@example.net"],
                "website": "http://www.george.net/",
                "insurance_provide_name": "Hall-Gilbert",
                "insurance_policy_number": "452972008732",
                "insurance_expiry_date": "1976-09-20",
                "tax_identity_type": "SSN",
                "tax_payer_id": "9396",
                "vendor_type_name": "single",
            },
            {
                "first_name": "Steven",
                "last_name": "Ward",
                "company_name": "Lane-Becker",
                "use_company_name_as_display_name": True,
                "vendor_type": 1,
                "gl_account": "16392591156",
                "personal_contact_numbers": ["+923111234455"],
                "business_contact_numbers": ["+923111234455"],
                "personal_emails": ["michelewilson@example.net"],
                "business_emails": ["ahayes@example.net"],
                "website": "http://www.george.net/",
                "insurance_provide_name": "Hall-Gilbert",
                "insurance_policy_number": "452972008732",
                "insurance_expiry_date": "1976-09-20",
                "tax_identity_type": "SSN",
                "tax_payer_id": "9396",
                "vendor_type_name": "single",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_vendor_serializer_write(vendor_type_factory, data, response, is_valid):
    """
    Testing :py:class:`people.serializers.VendorSerializer` write
    """

    vendor_type = vendor_type_factory(name="single")

    if is_valid:
        data["vendor_type"] = vendor_type.id
        response["vendor_type"] = vendor_type.id

    serializer = VendorSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_owner_people_serializer_read(owner_people_factory):
    """
    Testing :py:class:`people.serializers.OwnerPeopleSerializer` read
    """
    instance = owner_people_factory()

    serializer = OwnerPeopleSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["first_name"] == instance.first_name
    assert serializer.data["last_name"] == instance.last_name
    assert serializer.data["company_name"] == instance.company_name
    assert serializer.data["personal_contact_numbers"] == instance.personal_contact_numbers
    assert serializer.data["company_contact_numbers"] == instance.company_contact_numbers
    assert serializer.data["personal_emails"] == [str(i) for i in instance.personal_emails]
    assert serializer.data["company_emails"] == [str(i) for i in instance.company_emails]
    assert serializer.data["street_address"] == instance.street_address
    assert serializer.data["city"] == instance.city
    assert serializer.data["state"] == instance.state
    assert serializer.data["zip"] == instance.zip
    assert serializer.data["country"] == instance.country
    assert serializer.data["tax_payer"] == instance.tax_payer
    assert serializer.data["tax_payer_id"] == instance.tax_payer_id
    assert serializer.data["bank_account_title"] == instance.bank_account_title
    assert serializer.data["bank_name"] == instance.bank_name
    assert serializer.data["bank_branch"] == instance.bank_branch
    assert serializer.data["bank_routing_number"] == instance.bank_routing_number
    assert serializer.data["bank_account_number"] == instance.bank_account_number
    assert serializer.data["notes"] == instance.notes
    assert serializer.data["is_company_name_as_tax_payer"] == instance.is_company_name_as_tax_payer
    assert serializer.data["is_use_as_display_name"] == instance.is_use_as_display_name
    assert serializer.data.keys() == {
        "id",
        "first_name",
        "last_name",
        "company_name",
        "personal_contact_numbers",
        "company_contact_numbers",
        "personal_emails",
        "company_emails",
        "street_address",
        "city",
        "state",
        "zip",
        "country",
        "tax_payer",
        "tax_payer_id",
        "bank_account_title",
        "bank_name",
        "bank_branch",
        "bank_routing_number",
        "bank_account_number",
        "notes",
        "is_company_name_as_tax_payer",
        "is_use_as_display_name",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "first_name": ["This field is required."],
                "last_name": ["This field is required."],
                "personal_contact_numbers": ["This field is required."],
                "company_contact_numbers": ["This field is required."],
                "personal_emails": ["This field is required."],
                "company_emails": ["This field is required."],
                "tax_payer": ["This field is required."],
                "tax_payer_id": ["This field is required."],
            },
            False,
        ),
        (
            {
                "first_name": "Kevin",
                "last_name": "Jones",
                "company_name": "back",
                "personal_contact_numbers": ["+923111234455"],
                "company_contact_numbers": ["+923111234455"],
                "personal_emails": ["jamesandrea@example.com"],
                "company_emails": ["gabrielaspears@example.com"],
                "street_address": "561 Mosley Camp",
                "city": "New Jack",
                "state": "Connecticut",
                "zip": "74424",
                "country": "Botswana",
                "tax_payer": "Stephanie",
                "tax_payer_id": "255",
                "bank_account_title": "Hannah",
                "bank_name": "assume",
                "bank_branch": "North Mary",
                "bank_routing_number": "193",
                "bank_account_number": "653",
                "notes": "During star effort get such. Final find cost enter machine rate.",
                "is_company_name_as_tax_payer": True,
                "is_use_as_display_name": False,
            },
            {
                "first_name": "Kevin",
                "last_name": "Jones",
                "company_name": "back",
                "personal_contact_numbers": ["+923111234455"],
                "company_contact_numbers": ["+923111234455"],
                "personal_emails": ["jamesandrea@example.com"],
                "company_emails": ["gabrielaspears@example.com"],
                "street_address": "561 Mosley Camp",
                "city": "New Jack",
                "state": "Connecticut",
                "zip": "74424",
                "country": "Botswana",
                "tax_payer": "Stephanie",
                "tax_payer_id": "255",
                "bank_account_title": "Hannah",
                "bank_name": "assume",
                "bank_branch": "North Mary",
                "bank_routing_number": "193",
                "bank_account_number": "653",
                "notes": "During star effort get such. Final find cost enter machine rate.",
                "is_company_name_as_tax_payer": True,
                "is_use_as_display_name": False,
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_owner_people_serializer_write(data, response, is_valid):
    """
    Testing :py:class:`people.serializers.OwnerPeopleSerializer` write
    """

    serializer = OwnerPeopleSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_owner_upcoming_activity_serializer_read(owner_upcoming_activity_factory):
    """
    Testing :py:class:`people.serializers.OwnerUpcomingActivitySerializer` read
    """

    instance = owner_upcoming_activity_factory()

    serializer = OwnerUpcomingActivitySerializer(instance)
    assert serializer.data["id"] == instance.id
    assert serializer.data["title"] == instance.title
    assert serializer.data["description"] == instance.description
    assert serializer.data["date"] == instance.date
    assert serializer.data["start_time"] == instance.start_time
    assert serializer.data["end_time"] == instance.end_time
    assert serializer.data["label"] == instance.label.id
    assert serializer.data["assign_to"] == instance.assign_to.id
    assert serializer.data["status"] == instance.status
    assert serializer.data["owner"] == instance.owner.id
    assert serializer.data["label_name"] == instance.label.name
    assert serializer.data["assign_to_first_name"] == instance.assign_to.first_name
    assert serializer.data["assign_to_last_name"] == instance.assign_to.last_name
    assert serializer.data["assign_to_username"] == instance.assign_to.username
    assert serializer.data["owner_first_name"] == instance.owner.first_name
    assert serializer.data["owner_last_name"] == instance.owner.last_name
    assert serializer.data.keys() == {
        "id",
        "title",
        "description",
        "date",
        "start_time",
        "end_time",
        "label",
        "assign_to",
        "status",
        "owner",
        "label_name",
        "assign_to_first_name",
        "assign_to_last_name",
        "assign_to_username",
        "owner_first_name",
        "owner_last_name",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "title": ["This field is required."],
                "date": ["This field is required."],
                "owner": ["This field is required."],
            },
            False,
        ),
        (
            {
                "title": "lorem ipsum",
                "description": "lorem ipsum dolor",
                "date": "1977-08-31",
                "start_time": "14:23:03",
                "end_time": "14:23:03",
                "label": 1,
                "assign_to": 1,
                "status": False,
                "owner": 1,
            },
            {
                "title": "lorem ipsum",
                "description": "lorem ipsum dolor",
                "date": "1977-08-31",
                "start_time": "14:23:03",
                "end_time": "14:23:03",
                "label": 1,
                "assign_to": 1,
                "status": False,
                "owner": 1,
                "label_name": "Extra",
                "assign_to_first_name": "John",
                "assign_to_last_name": "Smith",
                "assign_to_username": "john_smith",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_owner_upcoming_activity_serializer_write(
    data, response, is_valid, owner_people_factory, user_factory, label_factory
):
    """
    Testing :py:class:`people.serializers.OwnerUpcomingActivitySerializer` write
    """

    owner = owner_people_factory()
    user = user_factory(first_name="John", last_name="Smith", username="john_smith")
    label = label_factory(name="Extra")

    if is_valid:
        data["owner"] = owner.id
        data["assign_to"] = user.id
        data["label"] = label.id
        response["owner"] = owner.id
        response["assign_to"] = user.id
        response["label"] = label.id
        response["owner_first_name"] = owner.first_name
        response["owner_last_name"] = owner.last_name

    serializer = OwnerUpcomingActivitySerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response
