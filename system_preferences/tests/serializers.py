import pytest

from ..serializers import (
    BusinessInformationSerializer,
    ContactCategorySerializer,
    InventoryItemTypeSerializer,
    InventoryLocationSerializer,
    LabelSerializer,
    ManagementFeeSerializer,
    PropertyTypeSerializer,
    TagSerializer,
)


@pytest.mark.django_db
def test_inventory_item_type_serializer_read(inventory_item_type_factory):
    """
    Testing :py:class:`system_preferences.serializers.InventoryItemTypeSerializer` read
    """
    instance = inventory_item_type_factory()

    serializer = InventoryItemTypeSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["name"] == instance.name


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        ({}, {"name": ["This field is required."]}, False),
        ({"name": "Furniture"}, {"name": "Furniture"}, True),
    ),
)
@pytest.mark.django_db
def test_invetory_item_type_serializer_write(data, response, is_valid):
    """
    Testing :py:class:`system_preferences.serializers.InventoryItemTypeSerializer` write
    """

    serializer = InventoryItemTypeSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_inventory_location_serializer_read(inventory_location_factory):
    """
    Testing :py:class:`system_preferences.serializers.InventoryLocationSerializer` read
    """

    instance = inventory_location_factory()
    serializer = InventoryLocationSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["name"] == instance.name


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        ({}, {"name": ["This field is required."]}, False),
        ({"name": "Islamabad"}, {"name": "Islamabad"}, True),
    ),
)
@pytest.mark.django_db
def test_inventory_location_serializer_write(data, response, is_valid):
    """
    Testing :py:class:`system_preferences.serializers.InventoryLocationSerializer` write
    """

    serializer = InventoryLocationSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_label_serializer_read(label_factory):
    """
    Testing :py:class:`system_preferences.serializers.LabelSerializer` read
    """

    instance = label_factory()
    serializer = LabelSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["name"] == instance.name


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        ({}, {"name": ["This field is required."]}, False),
        ({"name": "LoremLabel"}, {"name": "LoremLabel"}, True),
    ),
)
@pytest.mark.django_db
def test_label_serializer_write(data, response, is_valid):
    """
    Testing :py:class:`system_preferences.serializers.LabelSerializer` write
    """

    serializer = LabelSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_management_fee_serializer_read(management_fee_factory):
    """
    Testing :py:class:`system_preferences.serializers.ManagementFeeSerializer` read
    """

    instance = management_fee_factory()

    serializer = ManagementFeeSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["fee"] == str(instance.fee)
    assert serializer.data["fee_type"] == str(instance.fee_type)
    assert serializer.data["gl_account"] == instance.gl_account
    assert serializer.data["status"] == "ACTIVE"
    assert serializer.data["created_at"] is not None


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {"fee": "100.10", "fee_type": "FLAT_FEE"},
            {"gl_account": ["This field is required."]},
            False,
        ),
        (
            {"fee": "200.90", "gl_account": "PK-123-459"},
            {"fee_type": ["This field is required."]},
            False,
        ),
        (
            {"fee_type": "FLAT_FEE", "gl_account": "PK-123-999"},
            {"fee": ["This field is required."]},
            False,
        ),
        (
            {"fee": "100.00", "fee_type": "BY_PERCENTAGE", "gl_account": "PK-1234"},
            {
                "fee": "100.00",
                "fee_type": "BY_PERCENTAGE",
                "gl_account": "PK-1234",
                "previous_fee": None,
                "previous_fee_type": None,
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_management_fee_serializer_write(data, response, is_valid):
    """
    Testing :py:class:`system_preferences.serializers.ManagementFeeSerializer` write
    """

    serializer = ManagementFeeSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_tag_serializer_read(tag_factory):
    """
    Testing :py:class:`system_preferences.serializers.TagSerializer` read
    """

    instance = tag_factory()

    serializer = TagSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["name"] == instance.name


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        ({}, {"name": ["This field is required."]}, False),
        ({"name": "TestTag"}, {"name": "TestTag"}, True),
    ),
)
@pytest.mark.django_db
def test_tag_serializer_write(data, response, is_valid):
    """
    Testing :py:class:`system_preferences.serializers.TagSerializer` write
    """

    serializer = TagSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_property_type_serializer_read(property_type_factory):
    """
    Testing :py:class:`system_preferences.serializers.PropertyTypeSerializer` read
    """

    instance = property_type_factory()

    serializer = PropertyTypeSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["name"] == instance.name


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        ({}, {"name": ["This field is required."]}, False),
        ({"name": "Building"}, {"name": "Building"}, True),
    ),
)
@pytest.mark.django_db
def test_property_type_serializer_write(data, response, is_valid):
    """
    Testing :py:class:`system_preferences.serializers.PropertyTypeSerializer` write
    """

    serializer = PropertyTypeSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_business_information_serializer_read(business_information_factory):
    """
    Testing :py:class:`system_preferences.serializers.BusinessInformationSerializer` read
    """

    instance = business_information_factory()

    serializer = BusinessInformationSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["name"] == instance.name
    assert serializer.data["description"] == instance.description
    assert serializer.data["building_or_office_number"] == instance.building_or_office_number
    assert serializer.data["street"] == instance.street
    assert serializer.data["city"] == instance.city
    assert serializer.data["postal_code"] == instance.postal_code
    assert serializer.data["state"] == instance.state
    assert serializer.data["country"] == instance.country
    assert serializer.data["primary_email"] == instance.primary_email
    assert serializer.data["secondary_email"] == instance.secondary_email
    assert serializer.data["phone_number"] == instance.phone_number
    assert serializer.data["telephone_number"] == instance.telephone_number
    assert serializer.data["tax_identity_type"] == instance.tax_identity_type
    assert serializer.data["tax_payer_id"] == instance.tax_payer_id


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "logo": ["This field is required."],
                "name": ["This field is required."],
                "description": ["This field is required."],
                "building_or_office_number": ["This field is required."],
                "street": ["This field is required."],
                "city": ["This field is required."],
                "postal_code": ["This field is required."],
                "state": ["This field is required."],
                "country": ["This field is required."],
                "primary_email": ["This field is required."],
                "phone_number": ["This field is required."],
                "tax_identity_type": ["This field is required."],
                "tax_payer_id": ["This field is required."],
            },
            False,
        ),
        (
            {
                "logo": "http://www.smith.com/post/",
                "name": "Angelica Morales",
                "description": "Up military ball later allow interview",
                "building_or_office_number": "357",
                "street": "66874 Willis Center Suite 209",
                "city": "Jerrytown",
                "postal_code": "94067",
                "state": "SV",
                "country": "Guinea-Bissau",
                "primary_email": "kruegerpaula@example.com",
                "secondary_email": "veronicaharrell@example.net",
                "phone_number": "+1 (202) 555-9890",
                "telephone_number": "+1 (202) 555-9921",
                "tax_identity_type": "yard",
                "tax_payer_id": "pattern",
            },
            {
                "logo": "http://www.smith.com/post/",
                "name": "Angelica Morales",
                "description": "Up military ball later allow interview",
                "building_or_office_number": "357",
                "street": "66874 Willis Center Suite 209",
                "city": "Jerrytown",
                "postal_code": "94067",
                "state": "SV",
                "country": "Guinea-Bissau",
                "primary_email": "kruegerpaula@example.com",
                "secondary_email": "veronicaharrell@example.net",
                "phone_number": "+1 (202) 555-9890",
                "telephone_number": "+1 (202) 555-9921",
                "tax_identity_type": "yard",
                "tax_payer_id": "pattern",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_business_information_serializer_write(data, response, is_valid):
    """
    Testing :py:class:`system_preferences.serializers.BusinessInformationSerializer` write
    """

    serializer = BusinessInformationSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_contact_category_serializer_read(contact_category_factory):
    """
    Testing :py:class:`system_preferences.serializers.ContactCategorySerializer` read
    """
    instance = contact_category_factory()

    serializer = ContactCategorySerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["name"] == instance.name


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        ({}, {"name": ["This field is required."]}, False),
        ({"name": "Personal"}, {"name": "Personal"}, True),
    ),
)
@pytest.mark.django_db
def test_contact_category_serializer_write(data, response, is_valid):
    """
    Testing :py:class:`system_preferences.serializers.ContactCategorySerializer` write
    """

    serializer = ContactCategorySerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response
