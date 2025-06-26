from typing import Optional

from rest_framework import serializers

from core.serializers import ModifiedByAbstractSerializer
from property.models import Unit, UnitPhoto, UnitUpcomingActivity


class UnitPhotoSerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = UnitPhoto
        fields = ("id", "image", "unit", "is_cover")

    def create(self, validated_data):
        is_cover = validated_data.get("is_cover", False)
        if is_cover:
            UnitPhoto.objects.filter(unit=validated_data["unit"], is_cover=True).update(is_cover=False)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        is_cover = validated_data.get("is_cover", False)
        if is_cover:
            UnitPhoto.objects.filter(unit=instance.unit, is_cover=True).update(is_cover=False)
        return super().update(instance, validated_data)


class UnitUpcomingActivitySerializer(ModifiedByAbstractSerializer):
    label_name = serializers.CharField(source="label.name", read_only=True)
    assign_to_first_name = serializers.CharField(source="assign_to.first_name", read_only=True)
    assign_to_last_name = serializers.CharField(source="assign_to.last_name", read_only=True)
    assign_to_username = serializers.CharField(source="assign_to.username", read_only=True)
    unit_name = serializers.CharField(source="unit.name", read_only=True)

    class Meta:
        model = UnitUpcomingActivity
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
            "unit",
            "label_name",
            "assign_to_first_name",
            "assign_to_last_name",
            "assign_to_username",
            "unit_name",
        )


class UnitSerializer(ModifiedByAbstractSerializer):
    unit_type_name = serializers.CharField(source="unit_type.name", read_only=True)
    cover_picture = serializers.SerializerMethodField()
    cover_picture_id = serializers.SerializerMethodField()
    slug = serializers.CharField(read_only=True)
    is_occupied = serializers.BooleanField(read_only=True)
    lease_id = serializers.IntegerField(read_only=True)
    tenant_id = serializers.IntegerField(read_only=True)
    tenant_first_name = serializers.CharField(read_only=True)
    tenant_last_name = serializers.CharField(read_only=True)

    class Meta:
        model = Unit
        fields = (
            "id",
            "name",
            "slug",
            "unit_type",
            "market_rent",
            "future_market_rent",
            "effective_date",
            "application_fee",
            "tags",
            "estimate_turn_over_cost",
            "address",
            "ready_for_show_on",
            "virtual_showing_available",
            "utility_bills",
            "utility_bills_date",
            "lock_box",
            "description",
            "non_revenues_status",
            "balance",
            "total_charges",
            "total_credit",
            "due_amount",
            "total_payable",
            "parent_property",
            "unit_type_name",
            "cover_picture",
            "cover_picture_id",
            "is_occupied",
            "lease_id",
            "tenant_id",
            "tenant_first_name",
            "tenant_last_name",
        )
        read_only_fields = ("id", "parent_property")

    def get_cover_picture(self, obj):
        if isinstance(obj, Unit):
            cover_picture = Unit.objects.get_cover_picture(obj)
            if cover_picture:
                return cover_picture.image

    def get_cover_picture_id(self, obj):
        if isinstance(obj, Unit):
            cover_picture = Unit.objects.get_cover_picture(obj)
            if cover_picture:
                return cover_picture.id


class UnitListSerializer(ModifiedByAbstractSerializer):
    unit_type_name = serializers.CharField(source="unit_type.name", read_only=True)
    unit_type_bed_rooms = serializers.IntegerField(source="unit_type.bed_rooms", read_only=True)
    unit_type_bath_rooms = serializers.IntegerField(source="unit_type.bath_rooms", read_only=True)
    property_name = serializers.CharField(source="parent_property.name", read_only=True)
    cover_picture = serializers.SerializerMethodField()
    cover_picture_id = serializers.SerializerMethodField()
    is_occupied = serializers.BooleanField(read_only=True)
    slug = serializers.CharField(read_only=True)
    lease_start_date = serializers.SerializerMethodField()
    lease_end_date = serializers.SerializerMethodField()
    tenant_first_name = serializers.CharField(read_only=True)
    tenant_last_name = serializers.CharField(read_only=True)

    class Meta:
        model = Unit
        fields = (
            "id",
            "name",
            "slug",
            "unit_type",
            "is_occupied",
            "market_rent",
            "lease_start_date",
            "lease_end_date",
            "cover_picture",
            "cover_picture_id",
            "property_name",
            "tenant_first_name",
            "tenant_last_name",
            "unit_type_name",
            "unit_type_bed_rooms",
            "unit_type_bath_rooms",
        )

    def get_cover_picture(self, obj):
        if isinstance(obj, Unit):
            cover_picture = Unit.objects.get_cover_picture(obj)
            if cover_picture:
                return cover_picture.image

    def get_cover_picture_id(self, obj):
        if isinstance(obj, Unit):
            cover_picture = Unit.objects.get_cover_picture(obj)
            if cover_picture:
                return cover_picture.id

    def get_lease_start_date(self, obj) -> Optional[str]:
        lease = obj.leases.filter(status="ACTIVE").first()
        if lease:
            return lease.start_date
        else:
            return None

    def get_lease_end_date(self, obj) -> Optional[str]:
        lease = obj.leases.filter(status="ACTIVE").first()
        if lease:
            return lease.end_date
        else:
            return None
