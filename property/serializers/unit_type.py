from rest_framework import serializers

from core.serializers import ModifiedByAbstractSerializer
from property.models import UnitType, UnitTypePhoto


class UnitTypePhotoSerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = UnitTypePhoto
        fields = ("id", "image", "unit_type", "is_cover")

    def create(self, validated_data):
        is_cover = validated_data.get("is_cover", False)
        if is_cover:
            UnitTypePhoto.objects.filter(unit_type=validated_data["unit_type"], is_cover=True).update(is_cover=False)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        is_cover = validated_data.get("is_cover", False)
        if is_cover:
            UnitTypePhoto.objects.filter(unit_type=instance.unit_type, is_cover=True).update(is_cover=False)
        return super().update(instance, validated_data)


class UnitTypeSerializer(ModifiedByAbstractSerializer):
    cover_picture = serializers.SerializerMethodField()
    cover_picture_id = serializers.SerializerMethodField()
    apply_on_all_units = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = UnitType
        fields = (
            "id",
            "name",
            "bed_rooms",
            "bath_rooms",
            "square_feet",
            "market_rent",
            "future_market_rent",
            "effective_date",
            "application_fee",
            "tags",
            "estimate_turn_over_cost",
            "is_cat_allowed",
            "is_dog_allowed",
            "is_smoking_allowed",
            "marketing_title",
            "marketing_description",
            "marketing_youtube_url",
            "parent_property",
            "cover_picture",
            "cover_picture_id",
            "apply_on_all_units",
        )

    def get_cover_picture(self, obj):
        if isinstance(obj, UnitType):
            cover_picture = UnitType.objects.get_cover_picture(obj)
            if cover_picture:
                return cover_picture.image

    def get_cover_picture_id(self, obj):
        if isinstance(obj, UnitType):
            cover_picture = UnitType.objects.get_cover_picture(obj)
            if cover_picture:
                return cover_picture.id

    def create(self, validated_data):
        apply_on_all_units = validated_data.pop("apply_on_all_units", False)
        instance = super().create(validated_data)
        if apply_on_all_units:
            UnitType.objects.apply_on_all_units(instance)
        return instance

    def update(self, instance, validated_data):
        apply_on_all_units = validated_data.pop("apply_on_all_units", False)
        instance = super().update(instance, validated_data)
        if apply_on_all_units:
            UnitType.objects.apply_on_all_units(instance)
        return instance
