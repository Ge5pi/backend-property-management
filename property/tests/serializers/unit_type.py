import pytest

from property.serializers import UnitTypePhotoSerializer, UnitTypeSerializer


@pytest.mark.django_db
def test_unit_type_serializer_read(unit_type_factory):
    """
    Testing :py:class:`property.serializers.UnitTypeSerializer` read
    """
    unit_type = unit_type_factory()
    serializer = UnitTypeSerializer(unit_type)

    assert serializer.data == {
        "id": unit_type.id,
        "name": unit_type.name,
        "bed_rooms": unit_type.bed_rooms,
        "bath_rooms": unit_type.bath_rooms,
        "square_feet": unit_type.square_feet,
        "market_rent": str(unit_type.market_rent),
        "future_market_rent": str(unit_type.future_market_rent),
        "effective_date": unit_type.effective_date,
        "application_fee": str(unit_type.application_fee),
        "tags": [],
        "estimate_turn_over_cost": str(unit_type.estimate_turn_over_cost),
        "is_cat_allowed": unit_type.is_cat_allowed,
        "is_dog_allowed": unit_type.is_dog_allowed,
        "is_smoking_allowed": unit_type.is_smoking_allowed,
        "marketing_title": unit_type.marketing_title,
        "marketing_description": unit_type.marketing_description,
        "marketing_youtube_url": unit_type.marketing_youtube_url,
        "parent_property": unit_type.parent_property.id,
        "cover_picture": None,
        "cover_picture_id": None,
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "parent_property": ["This field is required."],
            },
            False,
        ),
        (
            {
                "name": "name",
                "bed_rooms": 1,
                "bath_rooms": 1,
                "square_feet": 1,
                "market_rent": 1,
                "effective_date": "2021-01-01",
                "application_fee": 1,
                "tags": [],
                "estimate_turn_over_cost": 1,
                "is_cat_allowed": True,
                "is_dog_allowed": True,
                "is_smoking_allowed": True,
                "marketing_title": "marketing_title",
                "marketing_description": "marketing_description",
                "parent_property": 1,
            },
            {
                "name": "name",
                "bed_rooms": 1,
                "bath_rooms": 1,
                "square_feet": 1,
                "market_rent": "1.00",
                "future_market_rent": None,
                "effective_date": "2021-01-01",
                "application_fee": "1.00",
                "tags": [],
                "estimate_turn_over_cost": "1.00",
                "is_cat_allowed": True,
                "is_dog_allowed": True,
                "is_smoking_allowed": True,
                "marketing_title": "marketing_title",
                "marketing_description": "marketing_description",
                "marketing_youtube_url": None,
                "parent_property": 1,
                "cover_picture": None,
                "cover_picture_id": None,
            },
            True,
        ),
    ),
)
def test_unit_type_serializer_write(data, response, is_valid, property_factory):
    """
    Testing :py:class:`property.serializers.UnitTypeSerializer` write
    """
    prop = property_factory()

    if is_valid:
        data["parent_property"] = prop.id
        response["parent_property"] = prop.id

    serializer = UnitTypeSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_unit_type_photo_serializer_read(unit_type_factory, unit_type_photo_factory):
    """
    Testing :py:class:`property.serializers.UnitTypePhotoSerializer` read
    """
    unit_type = unit_type_factory()
    instance = unit_type_photo_factory(unit_type=unit_type)

    serializer = UnitTypePhotoSerializer(instance)

    assert serializer.data == {
        "id": instance.id,
        "image": instance.image,
        "is_cover": instance.is_cover,
        "unit_type": instance.unit_type.id,
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "image": ["This field is required."],
                "unit_type": ["This field is required."],
            },
            False,
        ),
        (
            {
                "image": "image.jpg",
                "unit_type": 1,
            },
            {
                "image": "image.jpg",
                "unit_type": 1,
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_unit_type_photo_serializer_write(unit_type_factory, data, response, is_valid):
    """
    Testing :py:class:`property.serializers.UnitTypePhotoSerializer` write
    """

    unit_type = unit_type_factory()

    if is_valid:
        data["unit_type"] = unit_type.id
        response["unit_type"] = unit_type.id

    serializer = UnitTypePhotoSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response
