import pytest

from property.models import Unit
from property.serializers import (
    UnitListSerializer,
    UnitPhotoSerializer,
    UnitSerializer,
    UnitUpcomingActivitySerializer,
)


@pytest.mark.django_db
def test_unit_serializer_read(unit_factory):
    """
    Testing :py:class:`property.serializers.UnitSerializer` read
    """
    unit_factory()
    unit = Unit.objects.annotate_slug().annotate_data().get()
    serializer = UnitSerializer(unit)

    assert serializer.data == {
        "id": unit.id,
        "name": unit.name,
        "slug": unit.slug,
        "unit_type": unit.unit_type.id,
        "market_rent": str(unit.market_rent),
        "future_market_rent": str(unit.future_market_rent),
        "effective_date": str(unit.effective_date),
        "application_fee": str(unit.application_fee),
        "tags": [],
        "estimate_turn_over_cost": str(unit.estimate_turn_over_cost),
        "address": unit.address,
        "ready_for_show_on": str(unit.ready_for_show_on),
        "virtual_showing_available": unit.virtual_showing_available,
        "utility_bills": unit.utility_bills,
        "utility_bills_date": str(unit.utility_bills_date),
        "lock_box": unit.lock_box,
        "description": unit.description,
        "non_revenues_status": unit.non_revenues_status,
        "balance": str(unit.balance),
        "total_charges": str(unit.total_charges),
        "total_credit": str(unit.total_credit),
        "due_amount": str(unit.due_amount),
        "total_payable": str(unit.total_payable),
        "parent_property": unit.parent_property.id,
        "unit_type_name": unit.unit_type.name,
        "cover_picture": None,
        "cover_picture_id": None,
        "is_occupied": unit.is_occupied,
        "lease_id": unit.lease_id,
        "tenant_id": unit.tenant_id,
        "tenant_first_name": unit.tenant_first_name,
        "tenant_last_name": unit.tenant_last_name,
    }


@pytest.mark.django_db
def test_unit_list_serializer_read(unit_factory):
    """
    Testing :py:class:`property.serializers.UnitSerializer` read
    """
    unit_factory()
    unit = Unit.objects.annotate_slug().annotate_data().get()
    serializer = UnitListSerializer(unit)

    assert serializer.data == {
        "id": unit.id,
        "name": unit.name,
        "slug": unit.slug,
        "unit_type": unit.unit_type.id,
        "is_occupied": unit.is_occupied,
        "market_rent": str(unit.market_rent),
        "lease_start_date": None,
        "lease_end_date": None,
        "cover_picture": None,
        "cover_picture_id": None,
        "property_name": unit.parent_property.name,
        "tenant_first_name": unit.tenant_first_name,
        "tenant_last_name": unit.tenant_last_name,
        "unit_type_name": unit.unit_type.name,
        "unit_type_bed_rooms": unit.unit_type.bed_rooms,
        "unit_type_bath_rooms": unit.unit_type.bath_rooms,
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "unit_type": ["This field is required."],
            },
            False,
        ),
        (
            {
                "name": "name",
                "unit_type": 1,
                "market_rent": 1,
                "future_market_rent": 1,
                "effective_date": "2021-01-01",
                "application_fee": 1,
                "estimate_turn_over_cost": 1,
                "address": "address",
                "ready_for_show_on": "2021-01-01",
                "virtual_showing_available": True,
                "utility_bills": True,
                "utility_bills_date": "2021-01-01",
                "lock_box": "lock_box",
                "description": "description",
                "non_revenues_status": True,
                "balance": 1,
                "total_charges": 1,
                "total_credit": 1,
                "due_amount": 1,
                "total_payable": 1,
                "parent_property": 1,
            },
            {
                "name": "name",
                "market_rent": "1.00",
                "future_market_rent": "1.00",
                "effective_date": "2021-01-01",
                "application_fee": "1.00",
                "estimate_turn_over_cost": "1.00",
                "address": "address",
                "ready_for_show_on": "2021-01-01",
                "virtual_showing_available": True,
                "utility_bills": True,
                "utility_bills_date": "2021-01-01",
                "lock_box": "lock_box",
                "description": "description",
                "non_revenues_status": True,
                "balance": "1.00",
                "total_charges": "1.00",
                "total_credit": "1.00",
                "due_amount": "1.00",
                "total_payable": "1.00",
                "cover_picture": None,
                "cover_picture_id": None,
            },
            True,
        ),
    ),
)
def test_unit_serializer_write(data, response, is_valid, property_factory, unit_type_factory):
    """
    Testing :py:class:`property.serializers.UnitSerializer` write
    """
    prop = property_factory()
    unit_type = unit_type_factory(parent_property=prop)

    if is_valid:
        data["unit_type"] = unit_type.id
        response["unit_type"] = unit_type.id
        response["unit_type_name"] = unit_type.name

    serializer = UnitSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_unit_photo_serializer_read(unit_factory, unit_photo_factory):
    """
    Testing :py:class:`property.serializers.UnitPhotoSerializer` read
    """
    unit = unit_factory()
    instance = unit_photo_factory(unit=unit)

    serializer = UnitPhotoSerializer(instance)

    assert serializer.data == {
        "id": instance.id,
        "image": instance.image,
        "is_cover": instance.is_cover,
        "unit": instance.unit.id,
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "image": ["This field is required."],
                "unit": ["This field is required."],
            },
            False,
        ),
        (
            {
                "image": "image.jpg",
                "unit": 1,
            },
            {
                "image": "image.jpg",
                "unit": 1,
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_unit_photo_serializer_write(unit_factory, data, response, is_valid):
    """
    Testing :py:class:`property.serializers.UnitPhotoSerializer` write
    """

    unit = unit_factory()

    if is_valid:
        data["unit"] = unit.id
        response["unit"] = unit.id

    serializer = UnitPhotoSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_unit_upcoming_activity_serializer_read(unit_upcoming_activity_factory):
    """
    Testing :py:class:`property.serializers.UnitUpcomingActivitySerializer` read
    """

    instance = unit_upcoming_activity_factory()

    serializer = UnitUpcomingActivitySerializer(instance)
    assert serializer.data["id"] == instance.id
    assert serializer.data["description"] == instance.description
    assert serializer.data["date"] == instance.date
    assert serializer.data["start_time"] == instance.start_time
    assert serializer.data["end_time"] == instance.end_time
    assert serializer.data["label"] == instance.label.id
    assert serializer.data["assign_to"] == instance.assign_to.id
    assert serializer.data["status"] == instance.status
    assert serializer.data["unit"] == instance.unit.id
    assert serializer.data["label_name"] == instance.label.name
    assert serializer.data["assign_to_first_name"] == instance.assign_to.first_name
    assert serializer.data["assign_to_last_name"] == instance.assign_to.last_name
    assert serializer.data["assign_to_username"] == instance.assign_to.username
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
        "unit",
        "label_name",
        "assign_to_first_name",
        "assign_to_last_name",
        "assign_to_username",
        "unit_name",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "title": ["This field is required."],
                "date": ["This field is required."],
                "unit": ["This field is required."],
            },
            False,
        ),
        (
            {
                "title": "lorem",
                "description": "lorem ipsum dolor",
                "date": "1977-08-31",
                "start_time": "14:23:03",
                "end_time": "15:23:03",
                "label": 1,
                "assign_to": 1,
                "status": False,
                "unit": 1,
            },
            {
                "title": "lorem",
                "description": "lorem ipsum dolor",
                "date": "1977-08-31",
                "start_time": "14:23:03",
                "end_time": "15:23:03",
                "label": 1,
                "assign_to": 1,
                "status": False,
                "unit": 1,
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
def test_unit_upcoming_activity_serializer_write(data, response, is_valid, unit_factory, user_factory, label_factory):
    """
    Testing :py:class:`property.serializers.UnitUpcomingActivitySerializer` write
    """

    unit = unit_factory()
    user = user_factory(first_name="John", last_name="Smith", username="john_smith")
    label = label_factory(name="Extra")

    if is_valid:
        data["unit"] = unit.id
        data["assign_to"] = user.id
        data["label"] = label.id
        response["unit"] = unit.id
        response["assign_to"] = user.id
        response["label"] = label.id
        response["unit_name"] = unit.name

    serializer = UnitUpcomingActivitySerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response
