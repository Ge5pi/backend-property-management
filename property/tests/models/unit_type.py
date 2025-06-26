from decimal import Decimal

import pytest

from property.models import UnitType, UnitTypePhoto


@pytest.mark.django_db
def test_unit_type(unit_type_factory):
    """
    Testing :py:class:`property.models.UnitType` model with factory
    """
    unit_type = unit_type_factory(
        name="John's Unit Type",
        bed_rooms=2,
        bath_rooms=2,
        square_feet=1000,
        market_rent=Decimal("1000"),
        future_market_rent=Decimal("1100"),
        effective_date="2021-01-01",
        application_fee=Decimal("50"),
        estimate_turn_over_cost=Decimal("100"),
        is_cat_allowed=True,
        is_dog_allowed=True,
        is_smoking_allowed=True,
        marketing_title="Marketing Title",
        marketing_description="Marketing Description",
        marketing_youtube_url="https://www.youtube.com/watch?v=12345",
    )

    unit_types = UnitType.objects.all()
    assert unit_types.count() == 1
    assert unit_type.name == "John's Unit Type"
    assert unit_type.bed_rooms == 2
    assert unit_type.bath_rooms == 2
    assert unit_type.square_feet == 1000
    assert unit_type.market_rent == Decimal("1000")
    assert unit_type.future_market_rent == Decimal("1100")
    assert unit_type.effective_date == "2021-01-01"
    assert unit_type.application_fee == Decimal("50")
    assert unit_type.estimate_turn_over_cost == Decimal("100")
    assert unit_type.is_cat_allowed is True
    assert unit_type.is_dog_allowed is True
    assert unit_type.is_smoking_allowed is True
    assert unit_type.marketing_title == "Marketing Title"
    assert unit_type.marketing_description == "Marketing Description"
    assert unit_type.marketing_youtube_url == "https://www.youtube.com/watch?v=12345"

    assert str(unit_type) == "John's Unit Type"


@pytest.mark.django_db
def test_unit_type_photo(unit_type_photo_factory, unit_type_factory):
    """
    Testing :py:class:`property.models.UnitTypePhoto` model with factory
    """
    unit_type = unit_type_factory()
    unit_type_photo = unit_type_photo_factory(image="test.png", is_cover=False, unit_type=unit_type)

    unit_type_photos = UnitTypePhoto.objects.all()
    assert unit_type_photos.count() == 1
    assert unit_type_photo.image == "test.png"
    assert unit_type_photo.is_cover is False
    assert unit_type_photo.unit_type == unit_type
    assert str(unit_type_photo) == "test.png"
