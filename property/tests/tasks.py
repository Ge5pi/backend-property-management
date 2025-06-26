import pytest

from property.tasks import scheduled_rent_increase


@pytest.mark.django_db
def test_scheduled_rent_increase(property_factory, unit_type_factory, unit_factory):
    prop = property_factory()
    unit_type = unit_type_factory(
        parent_property=prop,
    )
    unit = unit_factory(unit_type=unit_type)
    unit.market_rent = 100
    unit.save()
    rent_increase = 50
    rent_increase_type = "percentage"
    scheduled_rent_increase(prop.id, rent_increase, rent_increase_type)
    unit.refresh_from_db()
    assert unit.market_rent == 150
    rent_increase = 100
    rent_increase_type = "fixed"
    scheduled_rent_increase(prop.id, rent_increase, rent_increase_type)
    unit.refresh_from_db()
    assert unit.market_rent == 250
