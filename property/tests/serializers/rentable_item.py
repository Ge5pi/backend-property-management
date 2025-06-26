import pytest

from property.serializers import RentableItemSerializer


@pytest.mark.django_db
def test_rentable_item_serializer_read(rentable_item_factory):
    """
    Testing :py:class:`property.serializers.RentableItemSerializer` read
    """
    rentable_item = rentable_item_factory()
    serializer = RentableItemSerializer(rentable_item)

    assert serializer.data == {
        "id": rentable_item.id,
        "name": rentable_item.name,
        "description": rentable_item.description,
        "amount": str(rentable_item.amount),
        "gl_account": rentable_item.gl_account,
        "tenant": rentable_item.tenant.id,
        "status": rentable_item.status,
        "parent_property": rentable_item.parent_property.id,
        "tenant_first_name": rentable_item.tenant.first_name,
        "tenant_last_name": rentable_item.tenant.last_name,
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "amount": ["This field is required."],
                "gl_account": ["This field is required."],
                "tenant": ["This field is required."],
                "parent_property": ["This field is required."],
            },
            False,
        ),
        (
            {
                "name": "Parking",
                "description": "Parking",
                "amount": 100,
                "gl_account": "123",
                "status": True,
            },
            {
                "name": "Parking",
                "description": "Parking",
                "amount": "100.00",
                "gl_account": "123",
                "status": True,
            },
            True,
        ),
    ),
)
def test_rentable_item_serializer_write(data, response, is_valid, property_factory, tenant_factory):
    """
    Testing :py:class:`property.serializers.UnitTypeSerializer` write
    """
    prop = property_factory()
    tenant = tenant_factory()

    if is_valid:
        data["parent_property"] = prop.id
        data["tenant"] = tenant.id
        response["parent_property"] = prop.id
        response["tenant"] = tenant.id
        response["tenant_first_name"] = tenant.first_name
        response["tenant_last_name"] = tenant.last_name

    serializer = RentableItemSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response
