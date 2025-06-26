from django.db.models import Max
from rest_framework import serializers

from authentication.serializers import UserSerializer
from core.serializers import ModifiedByAbstractSerializer
from people.models import Owner as PeopleOwner
from property.models import (
    Property,
    PropertyAttachment,
    PropertyLateFeePolicy,
    PropertyLeaseRenewalAttachment,
    PropertyLeaseTemplateAttachment,
    PropertyOwner,
    PropertyPhoto,
    PropertyUpcomingActivity,
    PropertyUtilityBilling,
)


class OwnerPeopleSerializerForPropertyList(ModifiedByAbstractSerializer):
    class Meta:
        model = PeopleOwner
        fields = ("id", "first_name", "last_name")


class PropertyUpcomingActivitySerializer(ModifiedByAbstractSerializer):
    label_name = serializers.CharField(source="label.name", read_only=True)
    assign_to_first_name = serializers.CharField(source="assign_to.first_name", read_only=True)
    assign_to_last_name = serializers.CharField(source="assign_to.last_name", read_only=True)
    assign_to_username = serializers.CharField(source="assign_to.username", read_only=True)
    parent_property_name = serializers.CharField(source="parent_property.name", read_only=True)

    class Meta:
        model = PropertyUpcomingActivity
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
            "parent_property",
            "label_name",
            "assign_to_first_name",
            "assign_to_last_name",
            "assign_to_username",
            "parent_property_name",
        )


class PropertyUtilityBillingSerializer(ModifiedByAbstractSerializer):
    vendor_full_name = serializers.CharField(source="vendor.full_name", read_only=True)

    class Meta:
        model = PropertyUtilityBilling
        fields = (
            "id",
            "utility",
            "vendor",
            "vendor_bill_gl",
            "tenant_charge_gl",
            "owner_contribution_percentage",
            "tenant_contribution_percentage",
            "parent_property",
            "vendor_full_name",
        )


class PropertyLateFeePolicySerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = PropertyLateFeePolicy
        fields = (
            "id",
            "start_date",
            "end_date",
            "late_fee_type",
            "get_late_fee_type_display",
            "base_amount_fee",
            "eligible_charges",
            "get_eligible_charges_display",
            "charge_daily_late_fees",
            "daily_amount_per_month_max",
            "grace_period_type",
            "grace_period",
        )


class PropertyAttachmentSerializer(ModifiedByAbstractSerializer):
    created_by = UserSerializer(many=False, read_only=True)

    class Meta:
        model = PropertyAttachment
        fields = (
            "id",
            "name",
            "created_by",
            "file",
            "parent_property",
            "file_type",
            "updated_at",
        )
        read_only_fields = ("id", "created_by")


class PropertyLeaseTemplateAttachmentSerializer(ModifiedByAbstractSerializer):
    created_by = UserSerializer(many=False, read_only=True)

    class Meta:
        model = PropertyLeaseTemplateAttachment
        fields = (
            "id",
            "name",
            "created_by",
            "file",
            "parent_property",
            "file_type",
            "updated_at",
        )
        read_only_fields = ("id", "created_by")


class PropertyLeaseRenewalAttachmentSerializer(ModifiedByAbstractSerializer):
    created_by = UserSerializer(many=False, read_only=True)

    class Meta:
        model = PropertyLeaseRenewalAttachment
        fields = (
            "id",
            "name",
            "created_by",
            "file",
            "parent_property",
            "file_type",
            "updated_at",
        )
        read_only_fields = ("id", "created_by")


class PropertyPhotoSerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = PropertyPhoto
        fields = ("id", "image", "is_cover", "parent_property")

    def create(self, validated_data):
        is_cover = validated_data.get("is_cover", False)
        if is_cover:
            PropertyPhoto.objects.filter(parent_property=validated_data["parent_property"], is_cover=True).update(
                is_cover=False
            )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        is_cover = validated_data.get("is_cover", False)
        if is_cover:
            PropertyPhoto.objects.filter(parent_property=instance.parent_property, is_cover=True).update(
                is_cover=False
            )
        return super().update(instance, validated_data)


class PropertyOwnerSerializer(ModifiedByAbstractSerializer):
    first_name = serializers.CharField(source="owner.first_name", read_only=True)
    last_name = serializers.CharField(source="owner.last_name", read_only=True)

    class Meta:
        model = PropertyOwner
        fields = (
            "id",
            "first_name",
            "last_name",
            "owner",
            "percentage_owned",
            "parent_property",
            "payment_type",
            "get_payment_type_display",
            "reserve_funds",
            "contract_expiry",
            "fiscal_year_end",
            "ownership_start_date",
        )


class PropertySerializer(ModifiedByAbstractSerializer):
    property_type_name = serializers.CharField(source="property_type.name", read_only=True)
    late_fee_base_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source="late_fee_policy.base_amount_fee"
    )
    cover_picture = serializers.SerializerMethodField()
    cover_picture_id = serializers.SerializerMethodField()
    slug = serializers.CharField(read_only=True)
    is_occupied = serializers.BooleanField(read_only=True)
    is_late_fee_policy_configured = serializers.BooleanField(read_only=True)
    number_of_units = serializers.IntegerField(read_only=True)
    is_occupied = serializers.BooleanField(read_only=True)
    is_late_fee_policy_configured = serializers.BooleanField(read_only=True)

    def get_cover_picture(self, obj):
        if isinstance(obj, Property):
            cover_picture = Property.objects.get_cover_picture(obj)
            if cover_picture:
                return cover_picture.image

    def get_cover_picture_id(self, obj):
        if isinstance(obj, Property):
            cover_picture = Property.objects.get_cover_picture(obj)
            if cover_picture:
                return cover_picture.id

    class Meta:
        model = Property
        fields = (
            "id",
            "name",
            "slug",
            "address",
            "property_type",
            "description",
            "renters_tax_location_code",
            "property_owner_license",
            "year_built",
            "management_start_date",
            "management_end_date",
            "management_end_reason",
            "nsf_fee",
            "management_fees_amount",
            "management_fees_percentage",
            "management_commission_type",
            "is_cat_allowed",
            "is_dog_allowed",
            "is_smoking_allowed",
            "additional_fees_gl_account",
            "additional_fees_percentage",
            "addition_fees_suppress",
            "notes",
            "tax_authority",
            "portfolio",
            "lease_fees_amount",
            "lease_fees_percentage",
            "lease_fees_commission_type",
            "maintenance_limit_amount",
            "insurance_expiration_date",
            "has_home_warranty_coverage",
            "home_warranty_company",
            "home_warranty_expiration_date",
            "maintenance_notes",
            "default_lease_template",
            "default_lease_agenda",
            "default_lease_renewal_template",
            "default_lease_renewal_agenda",
            "default_lease_renewal_letter_template",
            "late_fee_policy",
            "cover_picture",
            "cover_picture_id",
            "default_renewal_terms",
            "default_renewal_charge_by",
            "default_renewal_additional_fee",
            "rental_application_template",
            "is_occupied",
            "is_late_fee_policy_configured",
            "number_of_units",
            "is_occupied",
            "is_late_fee_policy_configured",
            "property_type_name",
            "late_fee_base_amount",
        )
        read_only_fields = ("id", "late_fee_policy")


class PropertyListSerializer(ModifiedByAbstractSerializer):
    cover_picture = serializers.SerializerMethodField()
    owner_peoples = serializers.SerializerMethodField()
    property_type = serializers.CharField(source="property_type.name")
    number_of_units = serializers.IntegerField(read_only=True)
    is_occupied = serializers.BooleanField(read_only=True)

    class Meta:
        model = Property
        fields = (
            "id",
            "name",
            "property_type",
            "number_of_units",
            "is_occupied",
            "cover_picture",
            "owner_peoples",
        )

    def get_cover_picture(self, obj):
        if isinstance(obj, Property):
            cover_picture = Property.objects.get_cover_picture(obj)
            if cover_picture:
                return cover_picture.image

    def get_owner_peoples(self, obj):
        owner_people_ids = obj.owners.values_list("owner")
        owner_people = PeopleOwner.objects.filter(id__in=owner_people_ids)
        return OwnerPeopleSerializerForPropertyList(owner_people, many=True).data


RENT_INCREASE_TYPE = (
    ("fixed", "Fixed"),
    ("percentage", "Percentage"),
)


class RentIncreaseSerializer(serializers.Serializer):
    rent_increase = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    rent_increase_type = serializers.ChoiceField(choices=RENT_INCREASE_TYPE, required=True)
    schedule_increase = serializers.BooleanField(required=True)
    schedule_increase_date = serializers.DateField(required=False)


class OwnerOwnedPropertiesListSerializer(ModifiedByAbstractSerializer):
    property_name = serializers.CharField(source="parent_property.name")
    number_of_units = serializers.IntegerField(read_only=True)

    class Meta:
        model = PropertyOwner
        fields = ("id", "percentage_owned", "property_name", "number_of_units")


class PortfolioPropertySerializer(ModifiedByAbstractSerializer):
    cover_picture = serializers.SerializerMethodField()
    vacant_for_days = serializers.SerializerMethodField()
    units_count = serializers.IntegerField(read_only=True)
    occupied_units_count = serializers.IntegerField(read_only=True)
    vacant_units_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Property
        fields = (
            "id",
            "name",
            "cover_picture",
            "units_count",
            "occupied_units_count",
            "vacant_units_count",
            "vacant_for_days",
        )

    def get_cover_picture(self, obj):
        if isinstance(obj, Property):
            cover_picture = Property.objects.get_cover_picture(obj)
            if cover_picture:
                return cover_picture.image

    def get_vacant_for_days(self, obj):
        return obj.units.annotate_data().aggregate(Max("vacant_for_days"))["vacant_for_days__max"]
