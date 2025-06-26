from typing import Any

from rest_framework import serializers

from authentication.serializers import UserSerializer
from core.serializers import ModifiedByAbstractSerializer
from property.serializers import UnitPhotoSerializer

from .models import (
    Area,
    AreaItem,
    FixedAsset,
    Inspection,
    Inventory,
    Labor,
    Project,
    ProjectExpense,
    ProjectExpenseAttachment,
    PurchaseOrder,
    PurchaseOrderAttachment,
    PurchaseOrderItem,
    ServiceRequest,
    ServiceRequestAttachment,
    WorkOrder,
)


class ServiceRequestSerializer(ModifiedByAbstractSerializer):
    property_id = serializers.IntegerField(source="unit.parent_property.id", read_only=True)
    property_name = serializers.CharField(source="unit.parent_property.name", read_only=True)
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    unit_cover_picture = serializers.SerializerMethodField()
    tenant_id = serializers.IntegerField(read_only=True)
    work_order_count = serializers.IntegerField(read_only=True)
    slug = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = ServiceRequest
        fields = (
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
        )

    def get_unit_cover_picture(self, obj):
        if isinstance(obj, Inspection):
            cover = obj.unit.photos.filter(is_cover=True).first()
            if cover:
                return UnitPhotoSerializer(cover).data
            else:
                cover = obj.unit.photos.all().first()
                if cover:
                    return UnitPhotoSerializer(cover).data

        return None


class ServiceRequestAttachmentSerializer(ModifiedByAbstractSerializer):
    created_by = UserSerializer(many=False, read_only=True)

    class Meta:
        model = ServiceRequestAttachment
        fields = (
            "id",
            "name",
            "created_by",
            "file",
            "service_request",
            "file_type",
            "updated_at",
        )
        read_only_fields = ("id", "created_by")


class LaborSerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = Labor
        fields = ("id", "title", "date", "hours", "description", "work_order")


class WorkOrderSerializer(ModifiedByAbstractSerializer):
    slug = serializers.CharField(read_only=True)
    property_name = serializers.CharField(source="service_request.unit.parent_property.name", read_only=True)
    property_id = serializers.IntegerField(source="service_request.unit.parent_property.id", read_only=True)
    assign_to_first_name = serializers.CharField(source="assign_to.first_name", read_only=True)
    assign_to_last_name = serializers.CharField(source="assign_to.last_name", read_only=True)
    assign_to_username = serializers.CharField(source="assign_to.username", read_only=True)

    class Meta:
        model = WorkOrder
        fields = (
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
            "assign_to_first_name",
            "assign_to_last_name",
            "assign_to_username",
        )
        read_only_fields = ("id", "property_name")


class InspectionSerializer(ModifiedByAbstractSerializer):
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    property_name = serializers.CharField(source="unit.parent_property.name", read_only=True)
    unit_cover_picture = serializers.SerializerMethodField()

    class Meta:
        model = Inspection
        fields = ["id", "name", "date", "unit", "unit_name", "property_name", "unit_cover_picture"]

    def get_unit_cover_picture(self, obj):
        if isinstance(obj, Inspection):
            cover = obj.unit.photos.filter(is_cover=True).first()
            if cover:
                return UnitPhotoSerializer(cover).data
            else:
                cover = obj.unit.photos.all().first()
                if cover:
                    return UnitPhotoSerializer(cover).data

        return None


class AreaSerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = Area
        fields = ["id", "name", "inspection"]


class AreaItemSerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = AreaItem
        fields = ["id", "name", "condition", "get_condition_display", "area"]


class ProjectSerializer(ModifiedByAbstractSerializer):
    parent_property_name = serializers.CharField(source="parent_property.name", read_only=True)

    class Meta:
        model = Project
        fields = [
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
        ]

    def create(self, validated_data):
        instance = super().create(validated_data)
        if instance.select_all_units:
            instance.units.clear()
            ids = list(instance.parent_property.units.all().values_list("id", flat=True))
            instance.units.add(*ids)

        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if instance.select_all_units:
            instance.units.clear()
            ids = list(instance.parent_property.units.all().values_list("id", flat=True))
            instance.units.add(*ids)

        return instance


class ProjectExpenseSerializer(ModifiedByAbstractSerializer):
    assigned_to_first_name = serializers.CharField(source="assigned_to.first_name", read_only=True)
    assigned_to_last_name = serializers.CharField(source="assigned_to.last_name", read_only=True)
    assigned_to_username = serializers.CharField(source="assigned_to.username", read_only=True)

    class Meta:
        model = ProjectExpense
        fields = (
            "id",
            "title",
            "amount",
            "date",
            "assigned_to",
            "project",
            "assigned_to_first_name",
            "assigned_to_last_name",
            "assigned_to_username",
        )


class ProjectExpenseAttachmentSerializer(ModifiedByAbstractSerializer):
    created_by = UserSerializer(many=False, read_only=True)

    class Meta:
        model = ProjectExpenseAttachment
        fields = (
            "id",
            "name",
            "created_by",
            "file",
            "project_expense",
            "file_type",
            "updated_at",
        )


class PurchaseOrderItemSerializer(ModifiedByAbstractSerializer):
    inventory_item_name = serializers.CharField(source="inventory_item.name", read_only=True)
    total_cost = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    tax_value = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    discount_value = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    item_cost = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = PurchaseOrderItem
        fields = (
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
        )
        read_only_fields = ("id", "total_cost", "cost")


class PurchaseOrderAttachmentSerializer(ModifiedByAbstractSerializer):
    created_by = UserSerializer(many=False, read_only=True)

    class Meta:
        model = PurchaseOrderAttachment
        fields = (
            "id",
            "name",
            "created_by",
            "file",
            "purchase_order",
            "file_type",
            "updated_at",
        )


class PurchaseOrderSerializer(ModifiedByAbstractSerializer):
    vendor_first_name = serializers.CharField(source="vendor.first_name", read_only=True)
    vendor_last_name = serializers.CharField(source="vendor.last_name", read_only=True)
    sub_total = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    tax_value = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    discount_value = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    shipping_value = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    total = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    slug = serializers.CharField(read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = (
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
            "sub_total",
            "tax_value",
            "discount_value",
            "shipping_value",
            "total",
            "created_at",
            "vendor_first_name",
            "vendor_last_name",
        )


class InventorySerializer(ModifiedByAbstractSerializer):
    item_type_name = serializers.CharField(source="item_type.name", read_only=True)
    location_name = serializers.CharField(source="location.name", read_only=True)

    class Meta:
        model = Inventory
        fields = (
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
        )

    def create(self, validated_data: Any) -> Any:
        validated_data["subscription"] = self.context["request"].user.associated_subscription
        return super().create(validated_data)


class InventoryUpdateSerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = Inventory
        fields = (
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
        )
        read_only_fields = ("id", "quantity")


class FixedAssetSerializer(ModifiedByAbstractSerializer):
    slug = serializers.CharField(read_only=True)
    inventory_name = serializers.CharField(source="inventory_item.name", read_only=True)
    inventory_location = serializers.CharField(source="inventory_item.location.name", read_only=True)
    total_cost = serializers.SerializerMethodField()
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    property_name = serializers.CharField(source="unit.parent_property.name", read_only=True)
    property_id = serializers.CharField(source="unit.parent_property.id", read_only=True)

    class Meta:
        model = FixedAsset
        fields = (
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
        )
        read_only_fields = ("id", "total_cost")

    def get_total_cost(self, obj):
        if isinstance(obj, FixedAsset):
            return obj.cost * obj.quantity
        else:
            return obj["cost"] * obj["quantity"]


class FixedAssetBulkCreateSerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = FixedAsset
        fields = (
            "id",
            "status",
            "placed_in_service_date",
            "warranty_expiration_date",
            "unit",
            "inventory_item",
            "quantity",
            "cost",
        )
        read_only_fields = ("id", "cost")

    def validate(self, attrs):
        inventory_item = attrs.get("inventory_item")
        if inventory_item.quantity < attrs.get("quantity"):
            attrs["error"] = f"Quantity must be less than or equal to {inventory_item.quantity}"
            raise serializers.ValidationError(attrs)
        return attrs

    def create(self, validated_data):
        validated_data["cost"] = validated_data["inventory_item"].cost
        validated_data["subscription"] = self.context["request"].user.associated_subscription
        return super().create(validated_data)
