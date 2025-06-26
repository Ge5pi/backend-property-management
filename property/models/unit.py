from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import CommonInfoAbstractModel, UpcomingActivityAbstract

from ..managers import UnitManager


class Unit(CommonInfoAbstractModel):
    SLUG = "unt"

    name = models.CharField(max_length=100)
    unit_type = models.ForeignKey("UnitType", related_name="units", on_delete=models.CASCADE)

    market_rent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    future_market_rent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    effective_date = models.DateField(blank=True, null=True)
    application_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tags = models.ManyToManyField("system_preferences.Tag", related_name="unit", blank=True)
    estimate_turn_over_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    address = models.TextField(blank=True, null=True)
    ready_for_show_on = models.DateField(blank=True, null=True)
    virtual_showing_available = models.BooleanField(default=False)
    utility_bills = models.BooleanField(default=False)
    utility_bills_date = models.DateField(blank=True, null=True)
    lock_box = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    non_revenues_status = models.BooleanField(default=False)

    balance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_charges = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_credit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_payable = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    parent_property = models.ForeignKey("Property", related_name="units", on_delete=models.CASCADE)

    objects = UnitManager()

    def save(self, *args, **kwargs):
        self.parent_property = self.unit_type.parent_property
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class UnitUpcomingActivity(UpcomingActivityAbstract, CommonInfoAbstractModel):
    unit = models.ForeignKey(Unit, related_name="upcoming_activities", on_delete=models.CASCADE)


class UnitPhoto(CommonInfoAbstractModel):
    image = models.CharField(max_length=2000)
    is_cover = models.BooleanField(default=False)
    unit = models.ForeignKey(Unit, related_name="photos", on_delete=models.CASCADE)

    def __str__(self):
        return self.image

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["unit"],
                condition=models.Q(is_cover=True),
                name="unit_unique_cover_pic",
                violation_error_message="Cover photo already exists for this unit",
            )
        ]


@receiver(post_save, sender=Unit)
def set_unit_type_info_in_unit(sender, instance, created, **kwargs):
    if created:
        instance.market_rent = instance.unit_type.market_rent
        instance.future_market_rent = instance.unit_type.future_market_rent
        instance.effective_date = instance.unit_type.effective_date
        instance.application_fee = instance.unit_type.application_fee
        instance.estimate_turn_over_cost = instance.unit_type.estimate_turn_over_cost
        instance.save()
