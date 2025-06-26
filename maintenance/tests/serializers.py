from decimal import Decimal

import pytest

from authentication.serializers import UserSerializer

from ..models import (
    Area,
    AreaItem,
    FixedAsset,
    Inspection,
    Labor,
    Project,
    ProjectExpense,
    PurchaseOrder,
    PurchaseOrderItem,
    ServiceRequest,
    WorkOrder,
)
from ..serializers import (
    AreaItemSerializer,
    AreaSerializer,
    FixedAssetBulkCreateSerializer,
    FixedAssetSerializer,
    InspectionSerializer,
    InventorySerializer,
    InventoryUpdateSerializer,
    LaborSerializer,
    ProjectExpenseAttachmentSerializer,
    ProjectExpenseSerializer,
    ProjectSerializer,
    PurchaseOrderAttachmentSerializer,
    PurchaseOrderItemSerializer,
    PurchaseOrderSerializer,
    ServiceRequestAttachmentSerializer,
    ServiceRequestSerializer,
    WorkOrderSerializer,
)


@pytest.mark.django_db
def test_inventory_serializer_read(inventory_factory):
    """
    Testing :py:class:`maintenance.serializers.InventorySerializer` read
    """
    instance = inventory_factory()

    serializer = InventorySerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["name"] == instance.name
    assert serializer.data["item_type"] == instance.item_type.id
    assert serializer.data["location"] == instance.location.id
    assert serializer.data["vendor"] == instance.vendor.id
    assert serializer.data["part_number"] == instance.part_number
    assert serializer.data["quantity"] == instance.quantity
    assert serializer.data["expense_account"] == instance.expense_account
    assert Decimal(serializer.data["cost"]) == instance.cost
    assert serializer.data["bin_or_shelf_number"] == instance.bin_or_shelf_number
    assert serializer.data["item_type_name"] == instance.item_type.name
    assert serializer.data["location_name"] == instance.location.name
    assert serializer.data.keys() == {
        "id",
        "name",
        "item_type",
        "description",
        "part_number",
        "vendor",
        "quantity",
        "expense_account",
        "cost",
        "location",
        "bin_or_shelf_number",
        "item_type_name",
        "location_name",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "description": ["This field is required."],
                "part_number": ["This field is required."],
                "quantity": ["This field is required."],
                "expense_account": ["This field is required."],
                "cost": ["This field is required."],
            },
            False,
        ),
        (
            {
                "name": "Fan",
                "item_type": 1,
                "description": "Read line shake short term.",
                "part_number": "2332",
                "vendor": 1,
                "quantity": 265229,
                "expense_account": "677121438893",
                "cost": "44.60",
                "location": 1,
                "bin_or_shelf_number": "8880",
            },
            {
                "name": "Fan",
                "item_type": 1,
                "description": "Read line shake short term.",
                "part_number": "2332",
                "vendor": 1,
                "quantity": 265229,
                "expense_account": "677121438893",
                "cost": "44.60",
                "location": 1,
                "bin_or_shelf_number": "8880",
                "item_type_name": "Item Type 1",
                "location_name": "Far peace.",
            },
            True,
        ),
        (
            {
                "name": "Fan",
                "description": "Read line shake short term.",
                "part_number": "2332",
                "quantity": 265229,
                "expense_account": "677121438893",
                "cost": "44.60",
                "bin_or_shelf_number": "8880",
            },
            {
                "name": "Fan",
                "description": "Read line shake short term.",
                "part_number": "2332",
                "quantity": 265229,
                "expense_account": "677121438893",
                "cost": "44.60",
                "bin_or_shelf_number": "8880",
                "item_type": None,
                "location": None,
                "vendor": None,
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_inventory_serializer_write(
    vendor_factory, inventory_item_type_factory, inventory_location_factory, data, response, is_valid
):
    """
    Testing :py:class:`maintenance.serializers.InventorySerializer` write
    """

    vendor = vendor_factory()
    inventory_type = inventory_item_type_factory(name="Item Type 1")
    location = inventory_location_factory(name="Far peace.")

    if is_valid:
        if "item_type" in data:
            data["item_type"] = inventory_type.id
            response["item_type"] = inventory_type.id
        if "location" in data:
            data["location"] = location.id
            response["location"] = location.id
        if "vendor" in data:
            data["vendor"] = vendor.id
            response["vendor"] = vendor.id

    serializer = InventorySerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "description": ["This field is required."],
                "part_number": ["This field is required."],
                "expense_account": ["This field is required."],
                "cost": ["This field is required."],
            },
            False,
        ),
        (
            {
                "name": "Fan",
                "item_type": 100,
                "description": "Read line shake short term.",
                "part_number": "2332",
                "vendor": 100,
                "expense_account": "677121438893",
                "cost": "44.60",
                "location": 100,
                "bin_or_shelf_number": "8880",
            },
            {
                "name": "Fan",
                "item_type": 100,
                "description": "Read line shake short term.",
                "part_number": "2332",
                "vendor": 100,
                "expense_account": "677121438893",
                "cost": "44.60",
                "location": 100,
                "bin_or_shelf_number": "8880",
            },
            True,
        ),
        (
            {
                "name": "Fan",
                "description": "Read line shake short term.",
                "part_number": "2332",
                "expense_account": "677121438893",
                "cost": "44.60",
                "bin_or_shelf_number": "8880",
            },
            {
                "name": "Fan",
                "item_type": None,
                "description": "Read line shake short term.",
                "part_number": "2332",
                "vendor": None,
                "expense_account": "677121438893",
                "cost": "44.60",
                "location": None,
                "bin_or_shelf_number": "8880",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_inventory_update_serializer_write(
    vendor_factory, inventory_item_type_factory, inventory_location_factory, data, response, is_valid
):
    """
    Testing :py:class:`maintenance.serializers.InventoryUpdateSerializer` write
    """

    vendor_factory(id=100)
    inventory_item_type_factory(id=100)
    inventory_location_factory(id=100)

    serializer = InventoryUpdateSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_fixed_asset_serializer_read(fixed_asset_factory):
    """
    Testing :py:class:`maintenance.serializers.FixedAssetSerializer` read
    """
    instance = fixed_asset_factory()
    fixed_asset = FixedAsset.objects.annotate_slug().get()  # type: ignore[attr-defined]

    serializer = FixedAssetSerializer(fixed_asset)

    assert serializer.data["id"] == instance.id
    assert serializer.data["status"] == instance.status
    assert serializer.data["get_status_display"] == instance.get_status_display()
    assert serializer.data["placed_in_service_date"] == instance.placed_in_service_date
    assert serializer.data["warranty_expiration_date"] == instance.warranty_expiration_date
    assert serializer.data["unit"] == instance.unit.id
    assert serializer.data["inventory_item"] == instance.inventory_item.id
    assert serializer.data["quantity"] == int(instance.quantity)
    assert Decimal(serializer.data["cost"]) == instance.cost
    assert serializer.data["unit_name"] == instance.unit.name
    assert serializer.data["property_name"] == instance.unit.parent_property.name
    assert serializer.data["property_id"] == str(instance.unit.parent_property.id)
    assert serializer.data["inventory_name"] == instance.inventory_item.name
    assert serializer.data["inventory_location"] == instance.inventory_item.location.name
    assert Decimal(serializer.data["total_cost"]) == instance.cost * instance.quantity
    assert serializer.data.keys() == {
        "id",
        "slug",
        "status",
        "get_status_display",
        "placed_in_service_date",
        "warranty_expiration_date",
        "unit",
        "inventory_item",
        "quantity",
        "cost",
        "unit_name",
        "property_name",
        "property_id",
        "inventory_name",
        "inventory_location",
        "total_cost",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "unit": ["This field is required."],
                "inventory_item": ["This field is required."],
                "quantity": ["This field is required."],
                "cost": ["This field is required."],
            },
            False,
        ),
        (
            {
                "status": "in_storage",
                "placed_in_service_date": "2020-01-01",
                "warranty_expiration_date": "2020-01-01",
                "unit": 100,
                "inventory_item": 100,
                "quantity": 9,
                "cost": "23.40",
            },
            {
                "status": "in_storage",
                "placed_in_service_date": "2020-01-01",
                "warranty_expiration_date": "2020-01-01",
                "unit": 100,
                "inventory_item": 100,
                "quantity": 9,
                "cost": "23.40",
                "unit_name": "Unit 1",
                "property_name": "Property 1",
                "property_id": "100",
                "inventory_name": "police",
                "inventory_location": "Far peace.",
                "total_cost": Decimal("210.60"),
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_fixed_asset_serializer_write(
    unit_factory,
    unit_type_factory,
    property_factory,
    inventory_factory,
    inventory_location_factory,
    data,
    response,
    is_valid,
):
    """
    Testing :py:class:`maintenance.serializers.FixedAssetSerializer` write
    """
    prop = property_factory(id=100, name="Property 1")
    unit_type = unit_type_factory(id=100, name="Unit Type 1", parent_property=prop)
    location = inventory_location_factory(id=100, name="Far peace.")
    unit_factory(id=100, unit_type=unit_type, name="Unit 1")
    inventory_factory(id=100, name="police", location=location, cost=Decimal("23.40"))

    serializer = FixedAssetSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_fixed_asset_bulk_create_serializer_read(fixed_asset_factory):
    """
    Testing :py:class:`maintenance.serializers.FixedAssetBulkCreateSerializer` read
    """
    instance = fixed_asset_factory()

    serializer = FixedAssetBulkCreateSerializer(instance)

    assert serializer.data["status"] == instance.status
    assert serializer.data["placed_in_service_date"] == instance.placed_in_service_date
    assert serializer.data["warranty_expiration_date"] == instance.warranty_expiration_date
    assert serializer.data["unit"] == instance.unit.id
    assert serializer.data["inventory_item"] == instance.inventory_item.id
    assert serializer.data["quantity"] == int(instance.quantity)
    assert serializer.data.keys() == {
        "id",
        "status",
        "placed_in_service_date",
        "warranty_expiration_date",
        "unit",
        "inventory_item",
        "quantity",
        "cost",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "unit": ["This field is required."],
                "inventory_item": ["This field is required."],
                "quantity": ["This field is required."],
            },
            False,
        ),
        (
            {
                "status": "in_storage",
                "placed_in_service_date": "2020-01-01",
                "warranty_expiration_date": "2020-01-01",
                "unit": 100,
                "inventory_item": 100,
                "quantity": 9,
            },
            {
                "status": "in_storage",
                "placed_in_service_date": "2020-01-01",
                "warranty_expiration_date": "2020-01-01",
                "unit": 100,
                "inventory_item": 100,
                "quantity": 9,
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_fixed_asset_bulk_create_serializer_write(
    unit_factory, unit_type_factory, property_factory, inventory_factory, data, response, is_valid
):
    """
    Testing :py:class:`maintenance.serializers.FixedAssetBulkCreateSerializer` write
    """
    prop = property_factory(id=100)
    unit_type = unit_type_factory(id=100, parent_property=prop)
    unit_factory(id=100, unit_type=unit_type)
    inventory_factory(id=100)

    serializer = FixedAssetBulkCreateSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_purchase_order_attachment_serializer_read(
    purchase_order_attachment_factory, user_factory, purchase_order_factory
):
    """
    Testing :py:class:`maintenance.serializers.PurchaseOrderAttachmentSerializer` read
    """
    purchase_order = purchase_order_factory()
    user = user_factory()
    instance = purchase_order_attachment_factory(created_by=user, purchase_order=purchase_order)
    serializer = PurchaseOrderAttachmentSerializer(instance)
    assert serializer.data["purchase_order"] == purchase_order.id
    assert serializer.data["created_by"] == UserSerializer(instance.created_by).data
    assert serializer.data["file"] == instance.file
    assert serializer.data["name"] == instance.name
    assert serializer.data["file_type"] == instance.file_type
    assert serializer.data["updated_at"] is not None
    assert serializer.data.keys() == {
        "id",
        "name",
        "created_by",
        "file",
        "purchase_order",
        "file_type",
        "updated_at",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "purchase_order": ["This field is required."],
                "name": ["This field is required."],
                "file": ["This field is required."],
                "file_type": ["This field is required."],
            },
            False,
        ),
        (
            {
                "purchase_order": 100,
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            {
                "purchase_order": 100,
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_purchase_order_attachment_serializer_write(purchase_order_factory, user_factory, data, response, is_valid):
    """
    Testing :py:class:`maintenance.serializers.PurchaseOrderAttachmentSerializer` write
    """
    purchase_order_factory(id=100)
    user_factory(id=100)
    serializer = PurchaseOrderAttachmentSerializer(data=data)
    assert serializer.is_valid() == is_valid
    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_purchase_order_item_serializer_read(purchase_order_item_factory, purchase_order_factory, inventory_factory):
    """
    Testing :py:class:`maintenance.serializers.PurchaseOrderItemSerializer` read
    """
    purchase_order = purchase_order_factory()
    inventory_item = inventory_factory(name="Fan")
    purchase_order_item_factory(purchase_order=purchase_order, inventory_item=inventory_item)
    instance = PurchaseOrderItem.objects.annotate_total_cost().get()
    serializer = PurchaseOrderItemSerializer(instance)

    assert serializer.data["purchase_order"] == purchase_order.id
    assert serializer.data["inventory_item"] == instance.inventory_item.id
    assert serializer.data["inventory_item_name"] == instance.inventory_item.name
    assert serializer.data["quantity"] == instance.quantity
    assert serializer.data["cost"] == str(instance.cost)
    assert serializer.data["total_cost"] == str(instance.total_cost)
    assert serializer.data["tax_value"] == str(instance.tax_value)
    assert serializer.data["discount_value"] == str(instance.discount_value)
    assert serializer.data["item_cost"] == str(instance.item_cost)

    assert serializer.data.keys() == {
        "id",
        "inventory_item_name",
        "inventory_item",
        "quantity",
        "cost",
        "purchase_order",
        "total_cost",
        "tax_value",
        "discount_value",
        "item_cost",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "purchase_order": ["This field is required."],
                "inventory_item": ["This field is required."],
                "quantity": ["This field is required."],
            },
            False,
        ),
        (
            {
                "purchase_order": 100,
                "inventory_item": 100,
                "quantity": 9,
            },
            {
                "purchase_order": 100,
                "inventory_item": 100,
                "quantity": 9,
                "inventory_item_name": "Fan",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_purchase_order_item_serializer_write(purchase_order_factory, inventory_factory, data, response, is_valid):
    """
    Testing :py:class:`maintenance.serializers.PurchaseOrderItemSerializer` write
    """
    purchase_order_factory(id=100)
    inventory_factory(id=100, name="Fan", cost="44.60")

    serializer = PurchaseOrderItemSerializer(data=data)

    assert serializer.is_valid() == is_valid
    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_purchase_order_serializer_read(purchase_order_factory, vendor_factory, property_factory):
    """
    Testing :py:class:`maintenance.serializers.PurchaseOrderSerializer` read
    """
    vendor = vendor_factory()
    instance = purchase_order_factory(vendor=vendor)
    purchase_order = (
        PurchaseOrder.objects.annotate_sub_total_and_total().annotate_slug().get()  # type: ignore[attr-defined]
    )

    serializer = PurchaseOrderSerializer(purchase_order)

    assert serializer.data["id"] == instance.id
    assert serializer.data["vendor"] == instance.vendor.id
    assert serializer.data["description"] == instance.description
    assert serializer.data["required_by_date"] == instance.required_by_date
    assert serializer.data["tax"] == str(instance.tax)
    assert serializer.data["tax_charge_type"] == instance.tax_charge_type
    assert serializer.data["get_tax_charge_type_display"] == instance.get_tax_charge_type_display()
    assert serializer.data["shipping"] == str(instance.shipping)
    assert serializer.data["shipping_charge_type"] == instance.shipping_charge_type
    assert serializer.data["get_shipping_charge_type_display"] == instance.get_shipping_charge_type_display()
    assert serializer.data["discount"] == str(instance.discount)
    assert serializer.data["discount_charge_type"] == instance.discount_charge_type
    assert serializer.data["get_discount_charge_type_display"] == instance.get_discount_charge_type_display()
    assert serializer.data["notes"] == instance.notes
    assert serializer.data["vendor_first_name"] == instance.vendor.first_name
    assert serializer.data["vendor_last_name"] == instance.vendor.last_name
    assert serializer.data["created_at"] is not None
    assert serializer.data.keys() == {
        "id",
        "slug",
        "vendor",
        "description",
        "required_by_date",
        "tax",
        "tax_charge_type",
        "get_tax_charge_type_display",
        "shipping",
        "shipping_charge_type",
        "get_shipping_charge_type_display",
        "discount",
        "discount_charge_type",
        "get_discount_charge_type_display",
        "notes",
        "vendor_first_name",
        "vendor_last_name",
        "sub_total",
        "tax_value",
        "discount_value",
        "shipping_value",
        "total",
        "created_at",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "description": ["This field is required."],
                "required_by_date": ["This field is required."],
            },
            False,
        ),
        (
            {
                "description": "Read line shake short term.",
                "required_by_date": "2020-01-01",
                "tax": "10",
                "tax_charge_type": "FLAT",
                "shipping": "10",
                "shipping_charge_type": "FLAT",
                "discount": "10",
                "discount_charge_type": "PERCENT",
                "notes": "Read line shake short term.",
            },
            {
                "description": "Read line shake short term.",
                "required_by_date": "2020-01-01",
                "tax": "10.00",
                "tax_charge_type": "FLAT",
                "shipping": "10.00",
                "shipping_charge_type": "FLAT",
                "discount": "10.00",
                "discount_charge_type": "PERCENT",
                "notes": "Read line shake short term.",
                "vendor_first_name": "Joanna",
                "vendor_last_name": "Brennan",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_purchase_order_serializer_write(vendor_factory, data, response, is_valid):
    """
    Testing :py:class:`maintenance.serializers.PurchaseOrderSerializer` write
    """
    vendor = vendor_factory(first_name="Joanna", last_name="Brennan")

    if is_valid:
        data["vendor"] = vendor.id
        response["vendor"] = vendor.id

    serializer = PurchaseOrderSerializer(data=data)

    assert serializer.is_valid() == is_valid
    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_work_order_serializer_read(work_order_factory):
    """
    Testing :py:class:`maintenance.serializers.WorkOrderSerializer` read
    """

    work_order_factory()
    work_order = WorkOrder.objects.annotate_slug().get()  # type: ignore[attr-defined]

    serializer = WorkOrderSerializer(work_order)

    assert serializer.data["id"] == work_order.id
    assert serializer.data["slug"] == f"{WorkOrder.SLUG}-{work_order.id}"
    assert serializer.data["is_recurring"] == work_order.is_recurring
    assert serializer.data["cycle"] == work_order.cycle
    assert serializer.data["status"] == work_order.status
    assert serializer.data["order_type"] == work_order.order_type
    assert serializer.data["get_order_type_display"] == work_order.get_order_type_display()
    assert serializer.data["get_status_display"] == work_order.get_status_display()
    assert serializer.data["get_cycle_display"] == work_order.get_cycle_display()
    assert serializer.data["job_description"] == work_order.job_description
    assert serializer.data["vendor_instructions"] == work_order.vendor_instructions
    assert serializer.data["vendor_trade"] == work_order.vendor_trade
    assert serializer.data["vendor_type"] == work_order.vendor_type.id
    assert serializer.data["vendor"] == work_order.vendor.id
    assert serializer.data["email_vendor"] == work_order.email_vendor
    assert serializer.data["assign_to"] == work_order.assign_to.id
    assert serializer.data["follow_up_date"] == str(work_order.follow_up_date)
    assert serializer.data["created_by"] == work_order.created_by
    assert serializer.data["service_request"] == work_order.service_request.id
    assert serializer.data["request_receipt"] == work_order.request_receipt
    assert serializer.data["owner_approved"] == work_order.owner_approved
    assert serializer.data["property_name"] == work_order.service_request.unit.parent_property.name
    assert serializer.data["property_id"] == work_order.service_request.unit.parent_property.id
    assert serializer.data["assign_to_first_name"] == work_order.assign_to.first_name
    assert serializer.data["assign_to_last_name"] == work_order.assign_to.last_name
    assert serializer.data["assign_to_username"] == work_order.assign_to.username
    assert serializer.data["created_at"] is not None
    assert serializer.data.keys() == {
        "id",
        "slug",
        "is_recurring",
        "cycle",
        "status",
        "order_type",
        "get_order_type_display",
        "get_status_display",
        "get_cycle_display",
        "job_description",
        "vendor_instructions",
        "vendor_trade",
        "vendor_type",
        "vendor",
        "email_vendor",
        "assign_to",
        "follow_up_date",
        "created_by",
        "created_at",
        "service_request",
        "request_receipt",
        "owner_approved",
        "property_name",
        "property_id",
        "created_at",
        "assign_to_first_name",
        "assign_to_last_name",
        "assign_to_username",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "order_type": ["This field is required."],
                "vendor_type": ["This field is required."],
                "vendor": ["This field is required."],
                "email_vendor": ["This field is required."],
                "follow_up_date": ["This field is required."],
                "service_request": ["This field is required."],
                "request_receipt": ["This field is required."],
                "owner_approved": ["This field is required."],
            },
            False,
        ),
        (
            {
                "is_recurring": False,
                "cycle": "MONTHLY",
                "status": "OPEN",
                "order_type": "RESIDENT",
                "job_description": "Color theory official game.",
                "vendor_instructions": "West rock drive onto attorney",
                "vendor_trade": "PLUMBER",
                "vendor_type": 100,
                "vendor": 100,
                "email_vendor": True,
                "assign_to": 100,
                "follow_up_date": "1987-01-12",
                "service_request": 100,
                "request_receipt": False,
                "owner_approved": False,
            },
            {
                "is_recurring": False,
                "cycle": "MONTHLY",
                "status": "OPEN",
                "order_type": "RESIDENT",
                "job_description": "Color theory official game.",
                "vendor_instructions": "West rock drive onto attorney",
                "vendor_trade": "PLUMBER",
                "vendor_type": 100,
                "vendor": 100,
                "email_vendor": True,
                "assign_to": 100,
                "follow_up_date": "1987-01-12",
                "service_request": 100,
                "request_receipt": False,
                "owner_approved": False,
                "property_name": "Fly place stage more myself",
                "property_id": 100,
                "assign_to_first_name": "John",
                "assign_to_last_name": "Smith",
                "assign_to_username": "john",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_work_order_serializer_write(
    vendor_type_factory,
    vendor_factory,
    user_factory,
    service_request_factory,
    unit_factory,
    unit_type_factory,
    property_factory,
    data,
    response,
    is_valid,
):
    """
    Testing :py:class:`maintenance.serializers.WorkOrderSerializer` write
    """

    vendor_type_factory(id=100)
    vendor_factory(id=100)
    user_factory(id=100, first_name="John", last_name="Smith", username="john")
    prop = property_factory(id=100, name="Fly place stage more myself")
    unit_type = unit_type_factory(parent_property=prop)
    unit = unit_factory(unit_type=unit_type)
    service_request_factory(id=100, unit=unit)

    serializer = WorkOrderSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_service_request_serializer_read(service_request_factory):
    """
    Testing :py:class:`maintenance.serializers.ServiceRequestSerializer` read
    """
    service_request_factory()
    instance = ServiceRequest.objects.annotate_slug().annotate_data().get()  # type: ignore[attr-defined]

    serializer = ServiceRequestSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["slug"] == f"{ServiceRequest.SLUG}-{instance.id}"
    assert serializer.data["unit"] == instance.unit.id
    assert serializer.data["order_type"] == instance.order_type
    assert serializer.data["get_order_type_display"] == instance.get_order_type_display()
    assert serializer.data["permission_to_enter"] == instance.permission_to_enter
    assert serializer.data["additional_information_for_entry"] == instance.additional_information_for_entry
    assert serializer.data["priority"] == instance.priority
    assert serializer.data["get_priority_display"] == instance.get_priority_display()
    assert serializer.data["subject"] == instance.subject
    assert serializer.data["description"] == instance.description
    assert serializer.data["property_id"] == instance.unit.parent_property.id
    assert serializer.data["tenant_id"] == instance.tenant_id
    assert serializer.data["work_order_count"] == instance.work_order_count
    assert serializer.data["property_name"] == instance.unit.parent_property.name
    assert serializer.data["unit_name"] == instance.unit.name
    assert serializer.data["unit_cover_picture"] is None
    assert serializer.data.keys() == {
        "id",
        "slug",
        "unit",
        "status",
        "order_type",
        "get_order_type_display",
        "permission_to_enter",
        "additional_information_for_entry",
        "priority",
        "get_priority_display",
        "subject",
        "description",
        "property_id",
        "tenant_id",
        "work_order_count",
        "property_name",
        "unit_name",
        "unit_cover_picture",
        "created_at",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "subject": ["This field is required."],
                "unit": ["This field is required."],
                "order_type": ["This field is required."],
                "priority": ["This field is required."],
                "description": ["This field is required."],
            },
            False,
        ),
        (
            {
                "subject": "Fan",
                "unit": 1,
                "order_type": "RESIDENT",
                "permission_to_enter": True,
                "additional_information_for_entry": "Read line shake short term.",
                "priority": "LOW",
                "description": "Read line shake short term.",
            },
            {
                "subject": "Fan",
                "order_type": "RESIDENT",
                "permission_to_enter": True,
                "additional_information_for_entry": "Read line shake short term.",
                "priority": "LOW",
                "description": "Read line shake short term.",
                "property_name": "Property 1",
                "unit_name": "Unit 1",
                "unit_cover_picture": None,
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_service_request_serializer_write(unit_factory, unit_type_factory, property_factory, data, response, is_valid):
    """
    Testing :py:class:`maintenance.serializers.ServiceRequestSerializer` write
    """
    prop = property_factory(name="Property 1")
    unit_type = unit_type_factory(id=100, parent_property=prop)
    unit = unit_factory(unit_type=unit_type, name="Unit 1")

    if is_valid:
        data["unit"] = unit.id
        response["property_id"] = prop.id
        response["unit"] = unit.id

    serializer = ServiceRequestSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_service_request_attachment_serializer_read(
    service_request_factory, service_request_attachment_factory, user_factory
):
    """
    Testing :py:class:`communication.serializers.ServiceRequestAttachmentSerializer` read
    """
    service_request = service_request_factory()
    user = user_factory()
    instance = service_request_attachment_factory(service_request=service_request, created_by=user)

    serializer = ServiceRequestAttachmentSerializer(instance)

    assert serializer.data["service_request"] == service_request.id
    assert serializer.data["created_by"] == UserSerializer(instance.created_by).data
    assert serializer.data["file"] == instance.file
    assert serializer.data["name"] == instance.name
    assert serializer.data["file_type"] == instance.file_type
    assert serializer.data["updated_at"] is not None
    assert serializer.data.keys() == {
        "id",
        "name",
        "created_by",
        "file",
        "service_request",
        "file_type",
        "updated_at",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "file": ["This field is required."],
                "service_request": ["This field is required."],
                "file_type": ["This field is required."],
            },
            False,
        ),
        (
            {
                "service_request": 100,
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            {
                "service_request": 100,
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_service_request_attachment_serializer_write(service_request_factory, data, response, is_valid):
    """
    Testing :py:class:`communication.serializers.ServiceRequestAttachmentSerializer` write
    """

    service_request_factory(id=100)

    serializer = ServiceRequestAttachmentSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_labor_serializer_read(labor_factory):
    """
    Testing :py:class:`maintenance.serializers.LaborSerializer` read
    """
    labor_factory()
    instance = Labor.objects.get()

    serializer = LaborSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["title"] == instance.title
    assert serializer.data["description"] == instance.description
    assert serializer.data["date"] == str(instance.date)
    assert serializer.data["hours"] == instance.hours
    assert serializer.data["work_order"] == instance.work_order.id

    assert serializer.data.keys() == {
        "id",
        "title",
        "description",
        "date",
        "hours",
        "work_order",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "title": ["This field is required."],
                "description": ["This field is required."],
                "date": ["This field is required."],
                "hours": ["This field is required."],
                "work_order": ["This field is required."],
            },
            False,
        ),
        (
            {
                "title": "Fan",
                "description": "Read line shake short term.",
                "date": "2020-01-01",
                "hours": 9,
            },
            {
                "title": "Fan",
                "description": "Read line shake short term.",
                "date": "2020-01-01",
                "hours": 9,
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_labor_serializer_write(work_order_factory, data, response, is_valid):
    """
    Testing :py:class:`maintenance.serializers.LaborSerializer` write
    """
    work_order = work_order_factory()

    if is_valid:
        data["work_order"] = work_order.id
        response["work_order"] = work_order.id

    serializer = LaborSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_inspection_serializer_read(inspection_factory):
    """
    Testing :py:class:`maintenance.serializers.InspectionSerializer` read
    """
    inspection_factory()
    instance = Inspection.objects.get()

    serializer = InspectionSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["name"] == instance.name
    assert serializer.data["date"] == str(instance.date)
    assert serializer.data["unit"] == instance.unit.id
    assert serializer.data["unit_name"] == instance.unit.name
    assert serializer.data["property_name"] == instance.unit.parent_property.name
    assert serializer.data["unit_cover_picture"] is None

    assert serializer.data.keys() == {"id", "name", "date", "unit", "unit_name", "property_name", "unit_cover_picture"}


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "date": ["This field is required."],
                "unit": ["This field is required."],
            },
            False,
        ),
        (
            {
                "name": "Fan",
                "date": "2020-01-01",
            },
            {
                "name": "Fan",
                "date": "2020-01-01",
                "unit_name": "Unit 1",
                "property_name": "Property 1",
                "unit_cover_picture": None,
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_inspection_serializer_write(unit_factory, unit_type_factory, property_factory, data, response, is_valid):
    """
    Testing :py:class:`maintenance.serializers.InspectionSerializer` write
    """
    prop = property_factory(name="Property 1")
    unit_type = unit_type_factory(id=100, parent_property=prop)
    unit = unit_factory(id=1, unit_type=unit_type, name="Unit 1")

    if is_valid:
        data["unit"] = unit.id
        response["unit"] = unit.id

    serializer = InspectionSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_area_serializer_read(area_factory):
    """
    Testing :py:class:`maintenance.serializers.AreaSerializer` read
    """
    area_factory()
    instance = Area.objects.get()

    serializer = AreaSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["name"] == instance.name
    assert serializer.data["inspection"] == instance.inspection.id

    assert serializer.data.keys() == {"id", "name", "inspection"}


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "inspection": ["This field is required."],
            },
            False,
        ),
        (
            {
                "name": "Fan",
            },
            {
                "name": "Fan",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_area_serializer_write(inspection_factory, data, response, is_valid):
    """
    Testing :py:class:`maintenance.serializers.AreaSerializer` write
    """
    inspection = inspection_factory()

    if is_valid:
        data["inspection"] = inspection.id
        response["inspection"] = inspection.id

    serializer = AreaSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_area_item_serializer_read(area_item_factory):
    """
    Testing :py:class:`maintenance.serializers.AreaItemSerializer` read
    """
    area_item_factory()
    instance = AreaItem.objects.get()

    serializer = AreaItemSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["name"] == instance.name
    assert serializer.data["condition"] == instance.condition
    assert serializer.data["get_condition_display"] == instance.get_condition_display()
    assert serializer.data["area"] == instance.area.id

    assert serializer.data.keys() == {"id", "name", "condition", "get_condition_display", "area"}


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "condition": ["This field is required."],
                "area": ["This field is required."],
            },
            False,
        ),
        (
            {
                "name": "Fan",
                "condition": "OKAY",
            },
            {
                "name": "Fan",
                "condition": "OKAY",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_area_item_serializer_write(area_factory, data, response, is_valid):
    """
    Testing :py:class:`maintenance.serializers.AreaItemSerializer` write
    """
    area = area_factory()

    if is_valid:
        data["area"] = area.id
        response["area"] = area.id

    serializer = AreaItemSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_project_serializer_read(project_factory, unit_factory):
    """
    Testing :py:class:`maintenance.serializers.ProjectSerializer` read
    """
    unit = unit_factory()
    project_factory(units=[unit])
    instance = Project.objects.get()

    serializer = ProjectSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["name"] == instance.name
    assert serializer.data["description"] == instance.description
    assert serializer.data["status"] == instance.status
    assert serializer.data["get_status_display"] == instance.get_status_display()
    assert serializer.data["parent_property"] == instance.parent_property.id
    assert serializer.data["units"] == [unit.id]
    assert serializer.data["select_all_units"] == instance.select_all_units
    assert serializer.data["budget"] == str(instance.budget)
    assert serializer.data["gl_account"] == instance.gl_account
    assert serializer.data["start_date"] == str(instance.start_date)
    assert serializer.data["end_date"] == str(instance.end_date)
    assert serializer.data["parent_property_name"] == instance.parent_property.name

    assert serializer.data.keys() == {
        "id",
        "name",
        "description",
        "status",
        "get_status_display",
        "parent_property",
        "units",
        "select_all_units",
        "budget",
        "gl_account",
        "start_date",
        "end_date",
        "parent_property_name",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "description": ["This field is required."],
                "parent_property": ["This field is required."],
                "select_all_units": ["This field is required."],
                "budget": ["This field is required."],
                "gl_account": ["This field is required."],
                "start_date": ["This field is required."],
            },
            False,
        ),
        (
            {
                "name": "Fan",
                "description": "Read line shake short term.",
                "status": "PENDING",
                "budget": "10.00",
                "gl_account": "12345",
                "start_date": "2020-01-01",
                "end_date": "2020-01-01",
                "select_all_units": False,
            },
            {
                "name": "Fan",
                "description": "Read line shake short term.",
                "status": "PENDING",
                "budget": "10.00",
                "gl_account": "12345",
                "start_date": "2020-01-01",
                "end_date": "2020-01-01",
                "parent_property_name": "Fly place stage more myself",
                "select_all_units": False,
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_project_serializer_write(property_factory, data, response, is_valid, unit_factory):
    """
    Testing :py:class:`maintenance.serializers.ProjectSerializer` write
    """
    prop = property_factory(id=1, name="Fly place stage more myself")
    unit = unit_factory()

    if is_valid:
        data["parent_property"] = prop.id
        data["units"] = [unit.id]
        response["parent_property"] = prop.id
        response["units"] = [unit.id]

    serializer = ProjectSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_project_expense_serializer_read(project_expense_factory, project_factory):
    """
    Testing :py:class:`maintenance.serializers.ProjectExpenseSerializer` read
    """
    project = project_factory()
    project_expense_factory(project=project)
    instance = ProjectExpense.objects.get()

    serializer = ProjectExpenseSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["title"] == instance.title
    assert serializer.data["amount"] == str(instance.amount)
    assert serializer.data["date"] == str(instance.date)
    assert serializer.data["assigned_to"] == instance.assigned_to.id
    assert serializer.data["project"] == instance.project.id
    assert serializer.data["assigned_to_first_name"] == instance.assigned_to.first_name
    assert serializer.data["assigned_to_last_name"] == instance.assigned_to.last_name
    assert serializer.data["assigned_to_username"] == instance.assigned_to.username

    assert serializer.data.keys() == {
        "id",
        "title",
        "amount",
        "date",
        "assigned_to",
        "project",
        "assigned_to_first_name",
        "assigned_to_last_name",
        "assigned_to_username",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "project": ["This field is required."],
                "title": ["This field is required."],
                "amount": ["This field is required."],
                "date": ["This field is required."],
                "assigned_to": ["This field is required."],
            },
            False,
        ),
        (
            {
                "title": "Fan",
                "amount": "10.00",
                "date": "2020-01-01",
            },
            {
                "title": "Fan",
                "amount": "10.00",
                "date": "2020-01-01",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_project_expense_serializer_write(project_factory, user_factory, data, response, is_valid):
    """
    Testing :py:class:`maintenance.serializers.ProjectExpenseSerializer` write
    """
    project = project_factory()
    user = user_factory()

    if is_valid:
        data["project"] = project.id
        data["assigned_to"] = user.id
        response["project"] = project.id
        response["assigned_to"] = user.id
        response["assigned_to_first_name"] = user.first_name
        response["assigned_to_last_name"] = user.last_name
        response["assigned_to_username"] = user.username

    serializer = ProjectExpenseSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_project_expense_attachment_serializer_read(
    project_expense_attachment_factory, user_factory, project_expense_factory
):
    """
    Testing :py:class:`maintenance.serializers.ProjectExpenseAttachmentSerializer` read
    """
    project_expense = project_expense_factory()
    user = user_factory()
    instance = project_expense_attachment_factory(created_by=user, project_expense=project_expense)
    serializer = ProjectExpenseAttachmentSerializer(instance)
    assert serializer.data["project_expense"] == project_expense.id
    assert serializer.data["created_by"] == UserSerializer(instance.created_by).data
    assert serializer.data["file"] == instance.file
    assert serializer.data["name"] == instance.name
    assert serializer.data["file_type"] == instance.file_type
    assert serializer.data["updated_at"] is not None
    assert serializer.data.keys() == {
        "id",
        "name",
        "created_by",
        "file",
        "project_expense",
        "file_type",
        "updated_at",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "project_expense": ["This field is required."],
                "name": ["This field is required."],
                "file": ["This field is required."],
                "file_type": ["This field is required."],
            },
            False,
        ),
        (
            {
                "project_expense": 100,
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            {
                "project_expense": 100,
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_project_expense_attachment_serializer_write(project_expense_factory, user_factory, data, response, is_valid):
    """
    Testing :py:class:`maintenance.serializers.ProjectExpenseAttachmentSerializer` write
    """
    project_expense_factory(id=100)
    user_factory(id=100)
    serializer = ProjectExpenseAttachmentSerializer(data=data)
    assert serializer.is_valid() == is_valid
    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response
