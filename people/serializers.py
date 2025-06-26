from rest_framework import serializers

from authentication.serializers import UserSerializer
from core.serializers import ModifiedByAbstractSerializer

from .models import (
    Owner,
    OwnerUpcomingActivity,
    Tenant,
    TenantAttachment,
    TenantUpcomingActivity,
    Vendor,
    VendorAddress,
    VendorAttachment,
    VendorType,
)


class TenantUpcomingActivitySerializer(ModifiedByAbstractSerializer):
    label_name = serializers.CharField(source="label.name", read_only=True)
    assign_to_first_name = serializers.CharField(source="assign_to.first_name", read_only=True)
    assign_to_last_name = serializers.CharField(source="assign_to.last_name", read_only=True)
    assign_to_username = serializers.CharField(source="assign_to.username", read_only=True)
    tenant_first_name = serializers.CharField(source="tenant.first_name", read_only=True)
    tenant_last_name = serializers.CharField(source="tenant.last_name", read_only=True)

    class Meta:
        model = TenantUpcomingActivity
        fields = (
            "id",
            "title",
            "description",
            "date",
            "start_time",
            "end_time",
            "label",
            "assign_to",
            "status",
            "tenant",
            "label_name",
            "assign_to_first_name",
            "assign_to_last_name",
            "assign_to_username",
            "tenant_first_name",
            "tenant_last_name",
        )


class TenantAttachmentSerializer(ModifiedByAbstractSerializer):
    created_by = UserSerializer(many=False, read_only=True)

    class Meta:
        model = TenantAttachment
        fields = (
            "id",
            "name",
            "created_by",
            "file",
            "file_type",
            "updated_at",
            "tenant",
        )
        read_only_fields = ("id", "created_by")


class TenantSerializer(ModifiedByAbstractSerializer):
    property_id = serializers.IntegerField(source="lease.unit.parent_property.id", read_only=True)
    property_name = serializers.CharField(source="lease.unit.parent_property.name", read_only=True)
    unit_id = serializers.IntegerField(source="lease.unit.id", read_only=True)
    unit_name = serializers.CharField(source="lease.unit.name", read_only=True)
    status = serializers.CharField(read_only=True)
    address = serializers.CharField(source="lease.unit.parent_property.address", read_only=True)
    rental_application_id = serializers.IntegerField(source="lease.rental_application.id", read_only=True)

    class Meta:
        model = Tenant
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "status",
            "property_name",
            "unit_name",
            "lease",
            "address",
            "property_id",
            "unit_id",
            "rental_application_id",
        )


class VendorTypeSerializer(ModifiedByAbstractSerializer):
    slug = serializers.CharField(read_only=True)
    vendor_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = VendorType
        fields = ("id", "name", "slug", "description", "vendor_count")


class VendorAddressSerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = VendorAddress
        fields = (
            "id",
            "street_address",
            "city",
            "state",
            "country",
            "zip",
            "vendor",
        )


class VendorAttachmentSerializer(ModifiedByAbstractSerializer):
    created_by = UserSerializer(many=False, read_only=True)

    class Meta:
        model = VendorAttachment
        fields = (
            "id",
            "name",
            "created_by",
            "file",
            "file_type",
            "updated_at",
            "vendor",
        )
        read_only_fields = ("id", "created_by")


class VendorSerializer(ModifiedByAbstractSerializer):
    slug = serializers.CharField(read_only=True)
    vendor_type_name = serializers.CharField(source="vendor_type.name", read_only=True)

    class Meta:
        model = Vendor
        fields = (
            "id",
            "first_name",
            "last_name",
            "slug",
            "company_name",
            "use_company_name_as_display_name",
            "vendor_type",
            "gl_account",
            "personal_contact_numbers",
            "business_contact_numbers",
            "personal_emails",
            "business_emails",
            "website",
            "insurance_provide_name",
            "insurance_policy_number",
            "insurance_expiry_date",
            "tax_identity_type",
            "get_tax_identity_type_display",
            "tax_payer_id",
            "vendor_type_name",
        )


class OwnerPeopleSerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = Owner
        fields = (
            "id",
            "first_name",
            "last_name",
            "company_name",
            "personal_contact_numbers",
            "company_contact_numbers",
            "personal_emails",
            "company_emails",
            "street_address",
            "city",
            "state",
            "zip",
            "country",
            "tax_payer",
            "tax_payer_id",
            "bank_account_title",
            "bank_name",
            "bank_branch",
            "bank_routing_number",
            "bank_account_number",
            "notes",
            "is_company_name_as_tax_payer",
            "is_use_as_display_name",
        )


class OwnerUpcomingActivitySerializer(ModifiedByAbstractSerializer):
    label_name = serializers.CharField(source="label.name", read_only=True)
    assign_to_first_name = serializers.CharField(source="assign_to.first_name", read_only=True)
    assign_to_last_name = serializers.CharField(source="assign_to.last_name", read_only=True)
    assign_to_username = serializers.CharField(source="assign_to.username", read_only=True)
    owner_first_name = serializers.CharField(source="owner.first_name", read_only=True)
    owner_last_name = serializers.CharField(source="owner.last_name", read_only=True)

    class Meta:
        model = OwnerUpcomingActivity
        fields = (
            "id",
            "title",
            "description",
            "date",
            "start_time",
            "end_time",
            "label",
            "assign_to",
            "status",
            "owner",
            "label_name",
            "assign_to_first_name",
            "assign_to_last_name",
            "assign_to_username",
            "owner_first_name",
            "owner_last_name",
        )
