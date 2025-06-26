import datetime
from decimal import Decimal

import pytest
from django.utils import timezone
from pytest import approx

from core.models import CommonInfoAbstractModel

from ..models import (
    BusinessInformation,
    ContactCategory,
    InventoryItemType,
    InventoryLocation,
    Label,
    ManagementFee,
    NameModelAbstract,
    PropertyType,
    Tag,
)


@pytest.mark.django_db
def test_property_type(property_type_factory):
    """
    Testing :py:class:`system_preferences.models.PropertyType` model with factory
    """

    property_type = property_type_factory(name="Apartment")

    property_types = PropertyType.objects.all()

    assert property_types.count() == 1
    assert property_type.pk is not None
    assert property_type.name == "Apartment"
    assert str(property_type) == "Apartment"
    assert issubclass(PropertyType, NameModelAbstract)
    assert issubclass(PropertyType, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_inventory_item_type(inventory_item_type_factory):
    """
    Testing :py:class:`system_preferences.models.InventoryItemType` model with factory
    """

    inventory_item_type = inventory_item_type_factory(name="Furniture")

    inventory_item_types = InventoryItemType.objects.all()

    assert inventory_item_types.count() == 1
    assert inventory_item_type.pk is not None
    assert inventory_item_type.name == "Furniture"
    assert str(inventory_item_type) == "Furniture"
    assert issubclass(InventoryItemType, NameModelAbstract)
    assert issubclass(InventoryItemType, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_tag(tag_factory):
    """
    Testing :py:class:`system_preferences.models.Tag` model with factory
    """

    tag = tag_factory(name="LoremTag")

    tags = Tag.objects.all()

    assert tags.count() == 1
    assert tag.pk is not None
    assert tag.name == "LoremTag"
    assert str(tag) == "LoremTag"
    assert issubclass(Tag, NameModelAbstract)
    assert issubclass(Tag, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_label(label_factory):
    """
    Testing :py:class:`system_preferences.models.Label` model with factory
    """

    label = label_factory(name="LoremLabel")

    labels = Label.objects.all()

    assert labels.count() == 1
    assert label.pk is not None
    assert label.name == "LoremLabel"
    assert str(label) == "LoremLabel"
    assert issubclass(Label, NameModelAbstract)
    assert issubclass(Label, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_inventory_location(inventory_location_factory):
    """
    Testing :py:class:`system_preferences.models.InventoryLocation` model with factory.
    """

    inventory_location = inventory_location_factory(name="San Francisco")

    inventory_locations = InventoryLocation.objects.all()

    assert inventory_locations.count() == 1
    assert inventory_location.pk is not None
    assert inventory_location.name == "San Francisco"
    assert str(inventory_location) == "San Francisco"
    assert issubclass(InventoryLocation, NameModelAbstract)
    assert issubclass(InventoryLocation, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_management_fee(management_fee_factory, freezer):
    """
    Testing :py:class:`system_preferences.models.ManagementFee` model with factory.
    """
    freezer.move_to("2020-01-01 00:00:00")
    management_fee = management_fee_factory(
        fee=Decimal("100.00"),
        fee_type="BY_PERCENTAGE",
        gl_account="PK-1234-789",
    )

    management_fees = ManagementFee.objects.all()

    assert management_fees.count() == 1
    assert management_fee.pk is not None
    assert management_fee.fee == approx(Decimal("100.00"))
    assert management_fee.fee_type == "BY_PERCENTAGE"
    assert management_fee.gl_account == "PK-1234-789"
    assert management_fee.status == "ACTIVE"
    assert management_fee.created_at == datetime.datetime(2020, 1, 1, 0, 0, tzinfo=timezone.get_current_timezone())
    assert str(management_fee) == management_fee.gl_account
    assert issubclass(ManagementFee, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_business_information(business_information_factory):
    """
    Testing :py:class:`system_preferences.models.BusinessInformation` models with factory
    """
    business_info = business_information_factory(
        logo="http://goodwin.biz/author.php",
        name="Moody Rock",
        description="Lorem ipsum dolor.",
        building_or_office_number="179-A",
        street="Angela Shoal Apt. 331",
        city="Morganburgh",
        state="LA",
        postal_code="82607",
        country="Samoa",
        primary_email="fruiz@example.net",
        secondary_email="hernandezpatricia@example.net",
        phone_number="+1-470-667-4673x098",
        telephone_number="(228)233-9890",
        tax_identity_type="what",
        tax_payer_id="sense",
    )

    business_infos = BusinessInformation.objects.all()
    assert business_infos.count() == 1
    assert business_info.logo == "http://goodwin.biz/author.php"
    assert business_info.name == "Moody Rock"
    assert business_info.description == "Lorem ipsum dolor."
    assert business_info.building_or_office_number == "179-A"
    assert business_info.street == "Angela Shoal Apt. 331"
    assert business_info.city == "Morganburgh"
    assert business_info.state == "LA"
    assert business_info.postal_code == "82607"
    assert business_info.country == "Samoa"
    assert business_info.primary_email == "fruiz@example.net"
    assert business_info.secondary_email == "hernandezpatricia@example.net"
    assert business_info.phone_number == "+1-470-667-4673x098"
    assert business_info.telephone_number == "(228)233-9890"
    assert business_info.tax_identity_type == "what"
    assert business_info.tax_payer_id == "sense"
    assert str(business_info) == business_info.name
    assert issubclass(BusinessInformation, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_contact_category(contact_category_factory):
    """
    Testing :py:class:`system_preferences.models.ContactCategory` model with factory
    """

    contact_category = contact_category_factory(name="Personal")

    contact_categories = ContactCategory.objects.all()

    assert contact_categories.count() == 1
    assert contact_category.pk is not None
    assert contact_category.name == "Personal"
    assert str(contact_category) == "Personal"
    assert issubclass(ContactCategory, NameModelAbstract)
    assert issubclass(ContactCategory, CommonInfoAbstractModel)
