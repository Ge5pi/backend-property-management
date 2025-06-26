from django.db import models
from phonenumber_field.modelfields import PhoneNumberField  # type: ignore[import]

from core.models import CommonInfoAbstractModel

from .managers import (
    ContactCategoryManager,
    InventoryItemTypeManager,
    InventoryLocationManager,
    LabelManager,
    PropertyTypeManager,
    TagManager,
)


class NameModelAbstract(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name


class PropertyType(NameModelAbstract, CommonInfoAbstractModel):
    objects = PropertyTypeManager()


class InventoryItemType(NameModelAbstract, CommonInfoAbstractModel):
    objects = InventoryItemTypeManager()


class Tag(NameModelAbstract, CommonInfoAbstractModel):
    objects = TagManager()


class Label(NameModelAbstract, CommonInfoAbstractModel):
    objects = LabelManager()


class InventoryLocation(NameModelAbstract, CommonInfoAbstractModel):
    objects = InventoryLocationManager()


class ManagementFee(CommonInfoAbstractModel):
    class FeeStatusChoices(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"

    class FeeTypeChoices(models.TextChoices):
        FLAT_FEE = "FLAT_FEE", "Flat Fee"
        BY_PERCENTAGE = "BY_PERCENTAGE", "By Percentage"

    fee = models.DecimalField(max_digits=10, decimal_places=2)
    fee_type = models.CharField(max_length=20, choices=FeeTypeChoices.choices)
    previous_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    previous_fee_type = models.CharField(max_length=20, choices=FeeTypeChoices.choices, blank=True, null=True)
    gl_account = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=FeeStatusChoices.choices)

    def __str__(self):
        return self.gl_account

    def save(self, *args, **kwargs) -> None:
        if self._state.adding:
            ManagementFee.objects.all().update(status=ManagementFee.FeeStatusChoices.INACTIVE)
            self.status = self.FeeStatusChoices.ACTIVE
            previous_obj = ManagementFee.objects.order_by("-created_at").first()
            if previous_obj:
                self.previous_fee = previous_obj.fee
                self.previous_fee_type = previous_obj.fee_type

        return super().save(*args, **kwargs)


class BusinessInformation(CommonInfoAbstractModel):
    logo = models.CharField(max_length=2000)
    name = models.CharField(max_length=100)
    description = models.TextField()
    building_or_office_number = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    primary_email = models.EmailField()
    secondary_email = models.EmailField(blank=True, null=True)
    phone_number = PhoneNumberField()
    telephone_number = PhoneNumberField(blank=True, null=True)
    tax_identity_type = models.CharField(max_length=100)
    tax_payer_id = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ContactCategory(NameModelAbstract, CommonInfoAbstractModel):
    objects = ContactCategoryManager()
