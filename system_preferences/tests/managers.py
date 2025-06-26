import pytest

from system_preferences.models import ContactCategory, InventoryItemType, InventoryLocation, Label, PropertyType, Tag


@pytest.mark.django_db
def test_annotate_num_records_of_property_type_manager(property_type_factory, property_factory):
    """
    Testing :py:meth:`system_preferences.managers.PropertyTypeManager.annotate_num_records`.
    """
    property_type = property_type_factory()
    property_factory(property_type=property_type)
    property_factory(property_type=property_type)
    property_factory(property_type=property_type)

    property_types = PropertyType.objects.annotate_num_records()

    assert property_types.get().items_count == 3


@pytest.mark.django_db
def test_annotate_num_records_of_tag_manager(tag_factory, unit_type_factory, note_factory, unit_factory):
    """
    Testing :py:meth:`system_preferences.managers.TagManager.annotate_num_records`.
    """
    tag = tag_factory()
    unit_type_factory.create(tags=(tag,))
    unit_type_factory.create(tags=(tag,))
    unit_type_factory.create(tags=(tag,))
    note_factory.create(tags=(tag,))
    note_factory.create(tags=(tag,))
    unit_factory.create(tags=(tag,))

    tags = Tag.objects.annotate_num_records()

    assert tags.get().items_count == 6


@pytest.mark.django_db
def test_annotate_num_records_of_label_manager(
    label_factory, property_upcoming_activity_factory, unit_upcoming_activity_factory
):
    """
    Testing :py:meth:`system_preferences.managers.TagManager.annotate_num_records`.
    """
    label = label_factory()
    property_upcoming_activity_factory(label=label)
    unit_upcoming_activity_factory(label=label)

    labels = Label.objects.annotate_num_records()

    assert labels.get().items_count == 2


@pytest.mark.django_db
def test_annotate_num_records_of_inventory_item_type_manager(inventory_item_type_factory, inventory_factory):
    """
    Testing :py:meth:`system_preferences.managers.InventoryItemTypeManager.annotate_num_records`.
    """
    item_type = inventory_item_type_factory()
    inventory_factory(item_type=item_type)
    inventory_factory(item_type=item_type)
    inventory_factory(item_type=item_type)

    item_types = InventoryItemType.objects.annotate_num_records()

    assert item_types.get().items_count == 3


@pytest.mark.django_db
def test_annotate_num_records_of_inventory_item_location_manager(inventory_location_factory, inventory_factory):
    """
    Testing :py:meth:`system_preferences.managers.InventoryLocationManager.annotate_num_records`.
    """
    item_location = inventory_location_factory()
    inventory_factory(location=item_location)
    inventory_factory(location=item_location)
    inventory_factory(location=item_location)

    item_locations = InventoryLocation.objects.annotate_num_records()

    assert item_locations.get().items_count == 3


@pytest.mark.django_db
def test_annotate_num_records_of_contact_category_manager(contact_category_factory, contact_factory):
    """
    Testing :py:meth:`system_preferences.managers.ContactCategoryManager.annotate_num_records`.
    """
    category = contact_category_factory()
    contact_factory(category=category)
    contact_factory(category=category)
    contact_factory(category=category)

    categories = ContactCategory.objects.annotate_num_records()

    assert categories.get().items_count == 3
