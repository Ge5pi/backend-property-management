import pytest

from property.models import RentableItem


@pytest.mark.django_db
def test_rentable_item(rentable_item_factory, property_factory):
    """
    Testing :py:class:`property.models.RentableItem` model with factory
    """
    prop = property_factory()
    rentable_item = rentable_item_factory(
        name="John's Rentable Item",
        description="Description",
        amount=1000,
        gl_account="1234",
        status=True,
        parent_property=prop,
    )

    rentable_items = RentableItem.objects.all()
    assert rentable_items.count() == 1
    assert rentable_item.name == "John's Rentable Item"
    assert rentable_item.description == "Description"
    assert rentable_item.amount == 1000
    assert rentable_item.gl_account == "1234"
    assert rentable_item.status is True
    assert rentable_item.parent_property == prop
    assert str(rentable_item) == "John's Rentable Item"
