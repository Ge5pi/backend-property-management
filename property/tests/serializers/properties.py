import pytest
from django.db.models import Max

from authentication.serializers import UserSerializer
from property.models import Property
from property.serializers import (
    OwnerOwnedPropertiesListSerializer,
    OwnerPeopleSerializerForPropertyList,
    PortfolioPropertySerializer,
    PropertyAttachmentSerializer,
    PropertyLateFeePolicySerializer,
    PropertyLeaseRenewalAttachmentSerializer,
    PropertyLeaseTemplateAttachmentSerializer,
    PropertyListSerializer,
    PropertyOwnerSerializer,
    PropertyPhotoSerializer,
    PropertySerializer,
    PropertyUpcomingActivitySerializer,
    PropertyUtilityBillingSerializer,
    RentIncreaseSerializer,
)


@pytest.mark.django_db
def test_property_upcoming_activity_serializer_read(property_upcoming_activity_factory):
    """
    Testing :py:class:`people.serializers.PropertyUpcomingActivitySerializer` read
    """

    instance = property_upcoming_activity_factory()

    serializer = PropertyUpcomingActivitySerializer(instance)
    assert serializer.data["id"] == instance.id
    assert serializer.data["title"] == instance.title
    assert serializer.data["description"] == instance.description
    assert serializer.data["date"] == instance.date
    assert serializer.data["start_time"] == instance.start_time
    assert serializer.data["end_time"] == instance.end_time
    assert serializer.data["label"] == instance.label.id
    assert serializer.data["assign_to"] == instance.assign_to.id
    assert serializer.data["status"] == instance.status
    assert serializer.data["parent_property"] == instance.parent_property.id
    assert serializer.data["label_name"] == instance.label.name
    assert serializer.data["assign_to_first_name"] == instance.assign_to.first_name
    assert serializer.data["assign_to_last_name"] == instance.assign_to.last_name
    assert serializer.data["assign_to_username"] == instance.assign_to.username
    assert serializer.data["parent_property_name"] == instance.parent_property.name
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
        "parent_property",
        "label_name",
        "assign_to_first_name",
        "assign_to_last_name",
        "assign_to_username",
        "parent_property_name",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "title": ["This field is required."],
                "date": ["This field is required."],
                "parent_property": ["This field is required."],
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
                "parent_property": 1,
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
                "parent_property": 1,
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
def test_property_upcoming_activity_serializer_write(
    data, response, is_valid, property_factory, user_factory, label_factory
):
    """
    Testing :py:class:`people.serializers.PropertyUpcomingActivitySerializer` write
    """

    prop = property_factory()
    user = user_factory(first_name="John", last_name="Smith", username="john_smith")
    label = label_factory(name="Extra")

    if is_valid:
        data["parent_property"] = prop.id
        data["assign_to"] = user.id
        data["label"] = label.id
        response["parent_property"] = prop.id
        response["assign_to"] = user.id
        response["label"] = label.id
        response["parent_property_name"] = prop.name

    serializer = PropertyUpcomingActivitySerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_property_attachment_serializer_read(property_factory, property_attachment_factory, user_factory):
    """
    Testing :py:class:`people.serializers.PropertyAttachmentSerializer` read
    """
    prop = property_factory()
    user = user_factory()
    instance = property_attachment_factory(parent_property=prop, created_by=user)

    serializer = PropertyAttachmentSerializer(instance)

    assert serializer.data["parent_property"] == prop.id
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
        "parent_property",
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
                "parent_property": ["This field is required."],
                "file_type": ["This field is required."],
            },
            False,
        ),
        (
            {
                "parent_property": 1,
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            {
                "parent_property": 1,
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_property_attachment_serializer_write(property_factory, data, response, is_valid):
    """
    Testing :py:class:`people.serializers.PropertyAttachmentSerializer` write
    """

    prop = property_factory()

    if is_valid:
        data["parent_property"] = prop.id
        response["parent_property"] = prop.id

    serializer = PropertyAttachmentSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_property_lease_template_attachment_serializer_read(
    property_factory, property_lease_template_attachment_factory, user_factory
):
    """
    Testing :py:class:`people.serializers.PropertyLeaseTemplateAttachmentSerializer` read
    """
    prop = property_factory()
    user = user_factory()
    instance = property_lease_template_attachment_factory(parent_property=prop, created_by=user)

    serializer = PropertyLeaseTemplateAttachmentSerializer(instance)

    assert serializer.data["parent_property"] == prop.id
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
        "parent_property",
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
                "parent_property": ["This field is required."],
                "file_type": ["This field is required."],
            },
            False,
        ),
        (
            {
                "parent_property": 1,
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            {
                "parent_property": 1,
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_property_lease_template_attachment_serializer_write(property_factory, data, response, is_valid):
    """
    Testing :py:class:`people.serializers.PropertyLeaseTemplateAttachmentSerializer` write
    """

    prop = property_factory()

    if is_valid:
        data["parent_property"] = prop.id
        response["parent_property"] = prop.id

    serializer = PropertyLeaseTemplateAttachmentSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_property_lease_renewal_attachment_serializer_read(
    property_factory, property_lease_renewal_attachment_factory, user_factory
):
    """
    Testing :py:class:`people.serializers.PropertyLeaseRenewalAttachmentSerializer` read
    """
    prop = property_factory()
    user = user_factory()
    instance = property_lease_renewal_attachment_factory(parent_property=prop, created_by=user)

    serializer = PropertyLeaseRenewalAttachmentSerializer(instance)

    assert serializer.data["parent_property"] == prop.id
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
        "parent_property",
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
                "parent_property": ["This field is required."],
                "file_type": ["This field is required."],
            },
            False,
        ),
        (
            {
                "parent_property": 1,
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            {
                "parent_property": 1,
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_property_lease_renewal_attachment_serializer_write(property_factory, data, response, is_valid):
    """
    Testing :py:class:`people.serializers.PropertyLeaseRenewalAttachmentSerializer` write
    """

    prop = property_factory()

    if is_valid:
        data["parent_property"] = prop.id
        response["parent_property"] = prop.id

    serializer = PropertyLeaseRenewalAttachmentSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_property_utility_billing_serializer_read(property_factory, property_utility_billing_factory):
    """
    Testing :py:class:`people.serializers.PropertyUtilityBillingSerializer` read
    """
    prop = property_factory()
    instance = property_utility_billing_factory(parent_property=prop)

    serializer = PropertyUtilityBillingSerializer(instance)

    assert serializer.data == {
        "id": instance.id,
        "utility": instance.utility,
        "vendor": instance.vendor.id,
        "vendor_bill_gl": str(instance.vendor_bill_gl),
        "tenant_charge_gl": str(instance.tenant_charge_gl),
        "owner_contribution_percentage": instance.owner_contribution_percentage,
        "tenant_contribution_percentage": instance.tenant_contribution_percentage,
        "parent_property": instance.parent_property.id,
        "vendor_full_name": instance.vendor.full_name,
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "utility": ["This field is required."],
                "vendor": ["This field is required."],
                "vendor_bill_gl": ["This field is required."],
                "tenant_charge_gl": ["This field is required."],
                "owner_contribution_percentage": ["This field is required."],
                "tenant_contribution_percentage": ["This field is required."],
                "parent_property": ["This field is required."],
            },
            False,
        ),
        (
            {
                "utility": "Electricity",
                "vendor": 1,
                "vendor_bill_gl": "123",
                "tenant_charge_gl": "456",
                "owner_contribution_percentage": 10,
                "tenant_contribution_percentage": 90,
                "parent_property": 1,
            },
            {
                "utility": "Electricity",
                "vendor": 1,
                "vendor_bill_gl": "123",
                "tenant_charge_gl": "456",
                "owner_contribution_percentage": 10,
                "tenant_contribution_percentage": 90,
                "parent_property": 1,
                "vendor_full_name": "John Smith",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_property_utility_billing_serializer_write(property_factory, data, response, is_valid, vendor_factory):
    """
    Testing :py:class:`people.serializers.PropertyUtilityBillingSerializer` write
    """

    prop = property_factory()
    vendor = vendor_factory(first_name="John", last_name="Smith")

    if is_valid:
        data["parent_property"] = prop.id
        data["vendor"] = vendor.id
        response["parent_property"] = prop.id
        response["vendor"] = vendor.id

    serializer = PropertyUtilityBillingSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_property_late_fee_policy_serializer_read(property_factory):
    """
    Testing :py:class:`people.serializers.PropertyLateFeePolicySerializer` read
    """
    prop = property_factory()
    instance = prop.late_fee_policy

    serializer = PropertyLateFeePolicySerializer(instance)

    assert serializer.data == {
        "id": instance.id,
        "start_date": instance.start_date,
        "end_date": instance.end_date,
        "late_fee_type": instance.late_fee_type,
        "get_late_fee_type_display": instance.get_late_fee_type_display(),
        "base_amount_fee": instance.base_amount_fee,
        "eligible_charges": instance.eligible_charges,
        "get_eligible_charges_display": instance.get_eligible_charges_display(),
        "charge_daily_late_fees": instance.charge_daily_late_fees,
        "daily_amount_per_month_max": instance.daily_amount_per_month_max,
        "grace_period_type": instance.grace_period_type,
        "grace_period": instance.grace_period,
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "start_date": None,
                "end_date": None,
                "late_fee_type": None,
                "base_amount_fee": None,
                "eligible_charges": None,
                "daily_amount_per_month_max": None,
                "grace_period_type": None,
                "grace_period": None,
            },
            True,
        ),
        (
            {
                "start_date": "2020-01-01",
                "end_date": "2020-12-31",
                "late_fee_type": "flat",
                "base_amount_fee": "100.00",
                "eligible_charges": "every_charge",
                "charge_daily_late_fees": True,
                "daily_amount_per_month_max": "100.00",
                "grace_period_type": "no_grace_period",
                "grace_period": 5,
            },
            {
                "start_date": "2020-01-01",
                "end_date": "2020-12-31",
                "late_fee_type": "flat",
                "base_amount_fee": "100.00",
                "eligible_charges": "every_charge",
                "charge_daily_late_fees": True,
                "daily_amount_per_month_max": "100.00",
                "grace_period_type": "no_grace_period",
                "grace_period": 5,
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_property_late_fee_policy_serializer_write(property_factory, data, response, is_valid):
    """
    Testing :py:class:`people.serializers.PropertyLateFeePolicySerializer` write
    """

    serializer = PropertyLateFeePolicySerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_property_photo_serializer_read(property_factory, property_photo_factory):
    """
    Testing :py:class:`people.serializers.PropertyPhotoSerializer` read
    """
    prop = property_factory()
    instance = property_photo_factory(parent_property=prop)

    serializer = PropertyPhotoSerializer(instance)

    assert serializer.data == {
        "id": instance.id,
        "image": instance.image,
        "is_cover": instance.is_cover,
        "parent_property": instance.parent_property.id,
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "image": ["This field is required."],
                "parent_property": ["This field is required."],
            },
            False,
        ),
        (
            {
                "image": "image.jpg",
                "parent_property": 1,
            },
            {
                "image": "image.jpg",
                "parent_property": 1,
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_property_photo_serializer_write(property_factory, data, response, is_valid):
    """
    Testing :py:class:`people.serializers.PropertyPhotoSerializer` write
    """

    prop = property_factory()

    if is_valid:
        data["parent_property"] = prop.id
        response["parent_property"] = prop.id

    serializer = PropertyPhotoSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_property_owner_serializer_read(property_factory, property_owner_factory):
    """
    Testing :py:class:`people.serializers.PropertyOwnerSerializer` read
    """
    prop = property_factory()
    instance = property_owner_factory(parent_property=prop)

    serializer = PropertyOwnerSerializer(instance)

    assert serializer.data == {
        "id": instance.id,
        "parent_property": instance.parent_property.id,
        "owner": instance.owner.id,
        "percentage_owned": instance.percentage_owned,
        "payment_type": instance.payment_type,
        "get_payment_type_display": instance.get_payment_type_display(),
        "reserve_funds": str(instance.reserve_funds),
        "contract_expiry": str(instance.contract_expiry),
        "fiscal_year_end": instance.fiscal_year_end,
        "ownership_start_date": str(instance.ownership_start_date),
        "first_name": instance.owner.first_name,
        "last_name": instance.owner.last_name,
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "owner": ["This field is required."],
                "percentage_owned": ["This field is required."],
                "parent_property": ["This field is required."],
                "payment_type": ["This field is required."],
                "reserve_funds": ["This field is required."],
                "contract_expiry": ["This field is required."],
                "fiscal_year_end": ["This field is required."],
                "ownership_start_date": ["This field is required."],
            },
            False,
        ),
        (
            {
                "owner": 1,
                "percentage_owned": 50,
                "parent_property": 1,
                "payment_type": "net_income",
                "reserve_funds": "1000.00",
                "contract_expiry": "2020-12-31",
                "fiscal_year_end": "2020-12-31",
                "ownership_start_date": "2020-01-01",
            },
            {
                "owner": 1,
                "percentage_owned": 50,
                "parent_property": 1,
                "payment_type": "net_income",
                "reserve_funds": "1000.00",
                "contract_expiry": "2020-12-31",
                "fiscal_year_end": "2020-12-31",
                "ownership_start_date": "2020-01-01",
                "first_name": "John",
                "last_name": "Smith",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_property_owner_serializer_write(property_factory, data, response, is_valid, owner_people_factory):
    """
    Testing :py:class:`people.serializers.PropertyOwnerSerializer` write
    """

    prop = property_factory()
    owner = owner_people_factory(first_name="John", last_name="Smith")

    if is_valid:
        data["parent_property"] = prop.id
        data["owner"] = owner.id
        response["parent_property"] = prop.id
        response["owner"] = owner.id

    serializer = PropertyOwnerSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_property_serializer_read(property_factory):
    """
    Testing :py:class:`people.serializers.PropertySerializer` read
    """
    instance = property_factory()
    instance = Property.objects.annotate_slug().annotate_data().get(id=instance.id)

    serializer = PropertySerializer(instance)

    assert serializer.data == {
        "id": instance.id,
        "name": instance.name,
        "slug": instance.slug,
        "address": instance.address,
        "property_type": instance.property_type.id,
        "description": instance.description,
        "renters_tax_location_code": instance.renters_tax_location_code,
        "property_owner_license": instance.property_owner_license,
        "year_built": instance.year_built,
        "management_start_date": str(instance.management_start_date),
        "management_end_date": str(instance.management_end_date),
        "management_end_reason": instance.management_end_reason,
        "nsf_fee": str(instance.nsf_fee),
        "management_fees_amount": str(instance.management_fees_amount),
        "management_fees_percentage": instance.management_fees_percentage,
        "management_commission_type": instance.management_commission_type,
        "is_cat_allowed": instance.is_cat_allowed,
        "is_dog_allowed": instance.is_dog_allowed,
        "is_smoking_allowed": instance.is_smoking_allowed,
        "additional_fees_gl_account": instance.additional_fees_gl_account,
        "additional_fees_percentage": instance.additional_fees_percentage,
        "addition_fees_suppress": instance.addition_fees_suppress,
        "notes": instance.notes,
        "tax_authority": instance.tax_authority,
        "portfolio": instance.portfolio,
        "lease_fees_amount": str(instance.lease_fees_amount),
        "lease_fees_percentage": instance.lease_fees_percentage,
        "lease_fees_commission_type": instance.lease_fees_commission_type,
        "maintenance_limit_amount": str(instance.maintenance_limit_amount),
        "insurance_expiration_date": str(instance.insurance_expiration_date),
        "has_home_warranty_coverage": instance.has_home_warranty_coverage,
        "home_warranty_company": instance.home_warranty_company,
        "home_warranty_expiration_date": str(instance.home_warranty_expiration_date),
        "maintenance_notes": instance.maintenance_notes,
        "default_lease_template": instance.default_lease_template.id,
        "default_lease_agenda": instance.default_lease_agenda,
        "default_lease_renewal_template": instance.default_lease_renewal_template.id,
        "default_lease_renewal_agenda": instance.default_lease_renewal_agenda,
        "default_lease_renewal_letter_template": instance.default_lease_renewal_letter_template,
        "late_fee_policy": instance.late_fee_policy.id,
        "cover_picture": None,
        "cover_picture_id": None,
        "default_renewal_terms": instance.default_renewal_terms,
        "default_renewal_charge_by": str(instance.default_renewal_charge_by),
        "default_renewal_additional_fee": str(instance.default_renewal_additional_fee),
        "rental_application_template": instance.rental_application_template.id,
        "is_occupied": instance.is_occupied,
        "number_of_units": instance.number_of_units,
        "is_late_fee_policy_configured": instance.is_late_fee_policy_configured,
        "property_type_name": instance.property_type.name,
        "late_fee_base_amount": instance.late_fee_policy.base_amount_fee,
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "address": ["This field is required."],
                "property_type": ["This field is required."],
            },
            False,
        ),
        (
            {
                "name": "Property",
                "address": "123 Main St",
                "property_type": 1,
                "description": "Lorem ipsum dolor sit amet",
                "renters_tax_location_code": "123",
                "property_owner_license": "123",
                "year_built": 1977,
                "management_start_date": "1977-08-31",
                "management_end_date": "1977-08-31",
                "management_end_reason": "End of management",
                "nsf_fee": "100.00",
                "management_fees_amount": "100.00",
                "management_fees_percentage": 10,
                "management_commission_type": "percentage",
                "is_cat_allowed": True,
                "is_dog_allowed": True,
                "is_smoking_allowed": True,
                "additional_fees_gl_account": "123",
                "additional_fees_percentage": 10,
                "addition_fees_suppress": True,
                "notes": "Lorem ipsum dolor sit amet",
                "tax_authority": "IRS",
                "portfolio": "123",
                "lease_fees_amount": "100.00",
                "lease_fees_percentage": 10,
                "lease_fees_commission_type": "percentage",
                "maintenance_limit_amount": "100.00",
                "insurance_expiration_date": "1977-08-31",
                "has_home_warranty_coverage": True,
                "home_warranty_company": "Home Warranty",
                "home_warranty_expiration_date": "1977-08-31",
                "maintenance_notes": "Lorem ipsum dolor sit amet",
                "default_lease_template": 1,
                "default_lease_agenda": "Lorem ipsum dolor sit amet",
                "default_lease_renewal_template": 1,
                "default_lease_renewal_agenda": "Lorem ipsum dolor sit amet",
                "default_lease_renewal_letter_template": "Lorem ipsum dolor sit amet",
                "cover_picture": None,
                "default_renewal_terms": "monthly",
                "default_renewal_charge_by": "200.00",
                "default_renewal_additional_fee": "100.00",
                "rental_application_template": 1,
            },
            {
                "name": "Property",
                "address": "123 Main St",
                "property_type": 1,
                "description": "Lorem ipsum dolor sit amet",
                "renters_tax_location_code": "123",
                "property_owner_license": "123",
                "year_built": 1977,
                "management_start_date": "1977-08-31",
                "management_end_date": "1977-08-31",
                "management_end_reason": "End of management",
                "nsf_fee": "100.00",
                "management_fees_amount": "100.00",
                "management_fees_percentage": 10,
                "management_commission_type": "percentage",
                "is_cat_allowed": True,
                "is_dog_allowed": True,
                "is_smoking_allowed": True,
                "additional_fees_gl_account": "123",
                "additional_fees_percentage": 10,
                "addition_fees_suppress": True,
                "notes": "Lorem ipsum dolor sit amet",
                "tax_authority": "IRS",
                "portfolio": "123",
                "lease_fees_amount": "100.00",
                "lease_fees_percentage": 10,
                "lease_fees_commission_type": "percentage",
                "maintenance_limit_amount": "100.00",
                "insurance_expiration_date": "1977-08-31",
                "has_home_warranty_coverage": True,
                "home_warranty_company": "Home Warranty",
                "home_warranty_expiration_date": "1977-08-31",
                "maintenance_notes": "Lorem ipsum dolor sit amet",
                "default_lease_template": 1,
                "default_lease_agenda": "Lorem ipsum dolor sit amet",
                "default_lease_renewal_template": 1,
                "default_lease_renewal_agenda": "Lorem ipsum dolor sit amet",
                "default_lease_renewal_letter_template": "Lorem ipsum dolor sit amet",
                "cover_picture": None,
                "cover_picture_id": None,
                "default_renewal_terms": "monthly",
                "default_renewal_charge_by": "200.00",
                "default_renewal_additional_fee": "100.00",
                "rental_application_template": 1,
                "property_type_name": "Apartment",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_property_serializer_write(
    data, response, is_valid, property_type_factory, lease_template_factory, rental_application_template_factory
):
    """
    Testing :py:class:`people.serializers.PropertySerializer` write
    """

    property_type = property_type_factory(name="Apartment")
    lease_template = lease_template_factory()
    rental_application_template = rental_application_template_factory()

    if is_valid:
        data["property_type"] = property_type.id
        data["default_lease_template"] = lease_template.id
        data["default_lease_renewal_template"] = lease_template.id
        data["rental_application_template"] = rental_application_template.id
        response["property_type"] = property_type.id
        response["default_lease_template"] = lease_template.id
        response["default_lease_renewal_template"] = lease_template.id
        response["rental_application_template"] = rental_application_template.id

    serializer = PropertySerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_people_owner_for_property_list_serializer_read(owner_people_factory):
    """
    Testing :py:class:`people.serializers.OwnerPeopleSerializerForPropertyList` read
    """
    instance = owner_people_factory()

    serializer = OwnerPeopleSerializerForPropertyList(instance)

    assert serializer.data == {
        "id": instance.id,
        "first_name": instance.first_name,
        "last_name": instance.last_name,
    }


@pytest.mark.django_db
def test_property_list_serializer_read(property_factory):
    """
    Testing :py:class:`people.serializers.PropertyListSerializer` read
    """
    instance = property_factory()
    instance = Property.objects.annotate_slug().annotate_data().get(id=instance.id)

    serializer = PropertyListSerializer(instance)

    assert serializer.data == {
        "id": instance.id,
        "name": instance.name,
        "property_type": instance.property_type.name,
        "number_of_units": instance.number_of_units,
        "is_occupied": instance.is_occupied,
        "cover_picture": None,
        "owner_peoples": OwnerPeopleSerializerForPropertyList(instance.owners, many=True).data,
    }


@pytest.mark.django_db
def test_owner_owned_properties_list_serializer_read(property_owner_factory):
    """
    Testing :py:class:`people.serializers.OwnerOwnedPropertiesListSerializer` read
    """
    instance = property_owner_factory()

    serializer = OwnerOwnedPropertiesListSerializer(instance)

    assert serializer.data == {
        "id": instance.id,
        "percentage_owned": instance.percentage_owned,
        "property_name": instance.parent_property.name,
    }


@pytest.mark.django_db
def test_portfolio_property_serializer_read(property_factory):
    """
    Testing :py:class:`people.serializers.PortfolioPropertySerializer` read
    """
    instance = property_factory()
    instance = Property.objects.annotate_slug().annotate_portfolio_data().get(id=instance.id)

    serializer = PortfolioPropertySerializer(instance)

    assert serializer.data == {
        "id": instance.id,
        "name": instance.name,
        "cover_picture": None,
        "units_count": instance.units_count,
        "occupied_units_count": instance.occupied_units_count,
        "vacant_units_count": instance.vacant_units_count,
        "vacant_for_days": instance.units.annotate_data().aggregate(Max("vacant_for_days"))["vacant_for_days__max"],
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "rent_increase": ["This field is required."],
                "rent_increase_type": ["This field is required."],
                "schedule_increase": ["This field is required."],
            },
            False,
        ),
        (
            {
                "rent_increase": "100.00",
                "rent_increase_type": "fixed",
                "schedule_increase": False,
                "schedule_increase_date": "2021-01-01",
            },
            {
                "rent_increase": "100.00",
                "rent_increase_type": "fixed",
                "schedule_increase": False,
                "schedule_increase_date": "2021-01-01",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_rent_increase_serializer_write(data, response, is_valid):
    """
    Testing :py:class:`people.serializers.RentIncreaseSerializer` write
    """

    serializer = RentIncreaseSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response
