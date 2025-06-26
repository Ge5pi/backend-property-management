from decimal import Decimal

import pytest

from property.models import Unit, UnitPhoto, UnitUpcomingActivity


@pytest.mark.django_db
def test_unit(unit_type_factory, unit_factory):
    """
    Testing :py:class:`property.models.Unit` model with factory
    """
    unit_type = unit_type_factory(
        market_rent=Decimal("1000"),
        future_market_rent=Decimal("1100"),
        effective_date="2021-01-01",
        application_fee=Decimal("50"),
        estimate_turn_over_cost=Decimal("100"),
    )
    unit = unit_factory(
        name="John's Unit Type",
        unit_type=unit_type,
        address="1234 Main St",
        ready_for_show_on="2021-01-01",
        virtual_showing_available=True,
        utility_bills=True,
        utility_bills_date="2021-01-01",
        lock_box="1234",
        description="Description",
        non_revenues_status=True,
        balance=Decimal("1000"),
        total_charges=Decimal("100"),
        total_credit=Decimal("100"),
        due_amount=Decimal("100"),
        total_payable=Decimal("100"),
    )

    units = Unit.objects.all()
    assert units.count() == 1
    assert unit.name == "John's Unit Type"
    assert unit.market_rent == Decimal("1000")
    assert unit.future_market_rent == Decimal("1100")
    assert unit.effective_date == "2021-01-01"
    assert unit.application_fee == Decimal("50")
    assert unit.estimate_turn_over_cost == Decimal("100")
    assert unit.address == "1234 Main St"
    assert unit.ready_for_show_on == "2021-01-01"
    assert unit.virtual_showing_available is True
    assert unit.utility_bills is True
    assert unit.utility_bills_date == "2021-01-01"
    assert unit.lock_box == "1234"
    assert unit.description == "Description"
    assert unit.non_revenues_status is True
    assert unit.balance == Decimal("1000")
    assert unit.total_charges == Decimal("100")
    assert unit.total_credit == Decimal("100")
    assert unit.due_amount == Decimal("100")
    assert unit.total_payable == Decimal("100")
    assert str(unit) == "John's Unit Type"


@pytest.mark.django_db
def test_unit_upcoming_activity(unit_upcoming_activity_factory, unit_factory, label_factory, user_factory):
    """
    Testing :py:class:`unit.models.unitUpcomingActivity` model with factory
    """

    unit = unit_factory()
    label = label_factory()
    assign_to = user_factory()
    upcoming_activity = unit_upcoming_activity_factory(
        title="Lorem",
        description="Mention put eat on son standard dream.",
        date="2023-12-12",
        start_time="17:23:51.297908",
        end_time="18:23:51.297908",
        label=label,
        assign_to=assign_to,
        unit=unit,
    )

    assert UnitUpcomingActivity.objects.count() == 1
    assert upcoming_activity.title == "Lorem"
    assert upcoming_activity.description == "Mention put eat on son standard dream."
    assert upcoming_activity.date == "2023-12-12"
    assert upcoming_activity.start_time == "17:23:51.297908"
    assert upcoming_activity.end_time == "18:23:51.297908"
    assert upcoming_activity.label == label
    assert upcoming_activity.assign_to == assign_to
    assert upcoming_activity.unit == unit
    assert str(upcoming_activity) == "Lorem"


@pytest.mark.django_db
def test_unit_photo(unit_photo_factory, unit_factory):
    """
    Testing :py:class:`property.models.UnitPhoto` model with factory
    """
    unit = unit_factory()
    unit_photo = unit_photo_factory(image="test.png", is_cover=False, unit=unit)

    unit_photos = UnitPhoto.objects.all()
    assert unit_photos.count() == 1
    assert unit_photo.image == "test.png"
    assert unit_photo.is_cover is False
    assert unit_photo.unit == unit
    assert str(unit_photo) == "test.png"
