from rest_framework import serializers

from core.serializers import ModifiedByAbstractSerializer

from .models import (
    BusinessInformation,
    ContactCategory,
    InventoryItemType,
    InventoryLocation,
    Label,
    ManagementFee,
    PropertyType,
    Tag,
)


class PropertyTypeSerializer(ModifiedByAbstractSerializer):
    items_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = PropertyType
        fields = ["id", "name", "items_count"]


class InventoryItemTypeSerializer(ModifiedByAbstractSerializer):
    items_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = InventoryItemType
        fields = ["id", "name", "items_count"]


class TagSerializer(ModifiedByAbstractSerializer):
    items_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tag
        fields = ["id", "name", "items_count"]


class LabelSerializer(ModifiedByAbstractSerializer):
    items_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Label
        fields = ["id", "name", "items_count"]


class InventoryLocationSerializer(ModifiedByAbstractSerializer):
    items_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = InventoryLocation
        fields = ["id", "name", "items_count"]


class ManagementFeeSerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = ManagementFee
        fields = (
            "id",
            "fee",
            "fee_type",
            "get_fee_type_display",
            "gl_account",
            "status",
            "get_status_display",
            "created_at",
            "created_by",
            "previous_fee",
            "previous_fee_type",
            "get_previous_fee_type_display",
        )
        read_only_fields = (
            "created_at",
            "created_by",
            "status",
            "previous_fee",
            "previous_fee_type",
        )


class BusinessInformationSerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = BusinessInformation
        fields = (
            "id",
            "logo",
            "name",
            "description",
            "building_or_office_number",
            "street",
            "city",
            "postal_code",
            "state",
            "country",
            "primary_email",
            "secondary_email",
            "phone_number",
            "telephone_number",
            "tax_identity_type",
            "tax_payer_id",
        )


class ContactCategorySerializer(ModifiedByAbstractSerializer):
    items_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ContactCategory
        fields = ["id", "name", "items_count"]
