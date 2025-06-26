from django.db import models

from core.models import CommonInfoAbstractModel
from property.managers import UnitTypeManager


class UnitType(CommonInfoAbstractModel):
    name = models.CharField(max_length=100)

    bed_rooms = models.IntegerField(blank=True, null=True)
    bath_rooms = models.IntegerField(blank=True, null=True)
    square_feet = models.IntegerField(blank=True, null=True)
    market_rent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    future_market_rent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    effective_date = models.DateField(blank=True, null=True)
    application_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tags = models.ManyToManyField("system_preferences.Tag", related_name="unit_types", blank=True)
    estimate_turn_over_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    is_cat_allowed = models.BooleanField(default=False)
    is_dog_allowed = models.BooleanField(default=False)
    is_smoking_allowed = models.BooleanField(default=False)

    marketing_title = models.CharField(max_length=100, blank=True, null=True)
    marketing_description = models.TextField(blank=True, null=True)
    marketing_youtube_url = models.CharField(max_length=2000, blank=True, null=True)
    parent_property = models.ForeignKey("Property", related_name="unit_types", on_delete=models.CASCADE)

    objects = UnitTypeManager()

    def __str__(self):
        return self.name


class UnitTypePhoto(CommonInfoAbstractModel):
    image = models.CharField(max_length=2000)
    is_cover = models.BooleanField(default=False)
    unit_type = models.ForeignKey(UnitType, related_name="photos", on_delete=models.CASCADE)

    def __str__(self):
        return self.image

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["unit_type"],
                condition=models.Q(is_cover=True),
                name="unit_type_unique_cover_pic",
                violation_error_message="Cover photo already exists for this unit type",
            )
        ]
