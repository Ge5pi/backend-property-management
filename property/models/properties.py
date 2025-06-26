import boto3  # type: ignore[import]
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from core.models import BaseAttachment, CommonInfoAbstractModel, UpcomingActivityAbstract
from property.managers import LateFeePolicyManager

from ..managers import PropertyManager


class PropertyUpcomingActivity(UpcomingActivityAbstract, CommonInfoAbstractModel):
    parent_property = models.ForeignKey(
        "Property",
        on_delete=models.CASCADE,
        related_name="upcoming_activities",
    )


class Property(CommonInfoAbstractModel):
    SLUG = "prp"

    class FeesType(models.TextChoices):
        PERCENTAGE = "percentage", "Percentage"
        FIXED = "fixed", "Fixed"

    class DefaultRenewalTerms(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        YEARLY = "yearly", "Yearly"

    name = models.CharField(max_length=255)
    address = models.TextField()
    property_type = models.ForeignKey(
        "system_preferences.PropertyType",
        related_name="properties",
        on_delete=models.CASCADE,
    )
    # Amenities
    is_cat_allowed = models.BooleanField(default=False)
    is_dog_allowed = models.BooleanField(default=False)
    is_smoking_allowed = models.BooleanField(default=False)
    # Additional Fees
    additional_fees_gl_account = models.CharField(max_length=255, blank=True, null=True)
    additional_fees_percentage = models.IntegerField(blank=True, null=True)
    addition_fees_suppress = models.BooleanField(default=False)
    # Lease Fees
    lease_fees_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    lease_fees_percentage = models.IntegerField(blank=True, null=True)
    lease_fees_commission_type = models.CharField(max_length=12, choices=FeesType.choices, blank=True, null=True)
    # Property information
    tax_authority = models.CharField(max_length=255, blank=True, null=True)
    portfolio = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    renters_tax_location_code = models.CharField(max_length=255, blank=True, null=True)
    property_owner_license = models.CharField(max_length=255, blank=True, null=True)
    year_built = models.IntegerField(blank=True, null=True)
    # Management Information
    management_start_date = models.DateField(blank=True, null=True)
    management_end_date = models.DateField(blank=True, null=True)
    management_end_reason = models.CharField(max_length=100, blank=True, null=True)
    # Rental Information:
    nsf_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    # Management Fees
    management_fees_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    management_fees_percentage = models.IntegerField(blank=True, null=True)
    management_commission_type = models.CharField(max_length=12, choices=FeesType.choices, blank=True, null=True)
    # Notes
    notes = models.TextField(blank=True, null=True)

    # Maintenance Information
    maintenance_limit_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    insurance_expiration_date = models.DateField(blank=True, null=True)
    has_home_warranty_coverage = models.BooleanField(default=False)
    home_warranty_company = models.CharField(max_length=255, blank=True, null=True)
    home_warranty_expiration_date = models.DateField(blank=True, null=True)
    maintenance_notes = models.TextField(blank=True, null=True)
    # Lease settings
    default_lease_template = models.ForeignKey(
        "lease.LeaseTemplate",
        related_name="default_lease_properties",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    default_lease_agenda = models.TextField(blank=True, null=True)

    default_lease_renewal_template = models.ForeignKey(
        "lease.LeaseTemplate",
        related_name="default_lease_renewal_properties",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    default_lease_renewal_agenda = models.TextField(blank=True, null=True)
    default_lease_renewal_letter_template = models.CharField(max_length=255, blank=True, null=True)

    default_renewal_terms = models.CharField(max_length=20, choices=DefaultRenewalTerms.choices, blank=True, null=True)
    default_renewal_charge_by = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    default_renewal_additional_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Rental Application Template
    rental_application_template = models.ForeignKey(
        "lease.RentalApplicationTemplate",
        related_name="properties",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    objects = PropertyManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Properties"


class PropertyUtilityBilling(CommonInfoAbstractModel):
    utility = models.CharField(max_length=255)
    vendor = models.ForeignKey("people.Vendor", related_name="utility_billings", on_delete=models.CASCADE)
    vendor_bill_gl = models.CharField(max_length=255)
    tenant_charge_gl = models.CharField(max_length=255)
    owner_contribution_percentage = models.IntegerField()
    tenant_contribution_percentage = models.IntegerField()
    parent_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="utility_billings")

    def __str__(self):
        return self.utility


class PropertyLateFeePolicy(CommonInfoAbstractModel):
    class LateFeeType(models.TextChoices):
        PERCENTAGE = "percentage", "Percentage"
        FLAT = "flat", "Flat"

    class EligibleCharges(models.TextChoices):
        EVERY_CHARGE = "every_charge", "Every Charge"
        ALL_RECURRING_CHARGES = "all_recurring_charges", "All Recurring Charges"
        ONLY_RECURRING_RENT = "only_recurring_rent", "Only Recurring Rent"

    class GracePeriodType(models.TextChoices):
        NUMBER_OF_DAY = "number_of_days", "Number of Days"
        TILL_DATE_OF_MONTH = "till_date_of_month", "Till Date of Month"
        NO_GRACE_PERIOD = "no_grace_period", "No Grace Period"

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    late_fee_type = models.CharField(max_length=20, choices=LateFeeType.choices, blank=True, null=True)
    base_amount_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    eligible_charges = models.CharField(max_length=21, choices=EligibleCharges.choices, blank=True, null=True)

    charge_daily_late_fees = models.BooleanField(default=False)
    daily_amount_per_month_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    grace_period_type = models.CharField(max_length=20, choices=GracePeriodType.choices, blank=True, null=True)
    grace_period = models.IntegerField(blank=True, null=True)

    parent_property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name="late_fee_policy")

    objects = LateFeePolicyManager()

    def __str__(self):
        return self.parent_property.name


class PropertyAttachment(BaseAttachment, CommonInfoAbstractModel):
    parent_property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="attachments",
    )

    class Meta:
        verbose_name_plural = "Attachments"

    def __str__(self):
        return self.name


class PropertyLeaseTemplateAttachment(BaseAttachment, CommonInfoAbstractModel):
    parent_property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="lease_template_attachments",
    )

    class Meta:
        verbose_name_plural = "Lease Template Attachments"

    def __str__(self):
        return self.name


class PropertyLeaseRenewalAttachment(BaseAttachment, CommonInfoAbstractModel):
    parent_property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="lease_renewal_attachments",
    )

    class Meta:
        verbose_name_plural = "Lease Renewal Attachments"

    def __str__(self):
        return self.name


class PropertyPhoto(CommonInfoAbstractModel):
    image = models.CharField(max_length=2000)
    is_cover = models.BooleanField(default=False)
    parent_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="photos")

    def __str__(self):
        return self.image

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["parent_property"],
                condition=models.Q(is_cover=True),
                name="property_unique_cover_pic",
                violation_error_message="Cover photo already exists for this property",
            )
        ]


class PropertyOwner(CommonInfoAbstractModel):
    class PaymentTypeChoices(models.TextChoices):
        NET_INCOME = "net_income", "Net Income"
        FLAT = "flat", "Flat"

    percentage_owned = models.PositiveIntegerField(validators=[MaxValueValidator(100), MinValueValidator(1)])
    parent_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="owners")
    payment_type = models.CharField(max_length=12, choices=PaymentTypeChoices.choices)
    contract_expiry = models.DateField()
    reserve_funds = models.DecimalField(max_digits=10, decimal_places=2)
    fiscal_year_end = models.CharField(max_length=50)
    ownership_start_date = models.DateField()
    owner = models.ForeignKey("people.Owner", related_name="owned_properties", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.owner)

    class Meta:
        unique_together = ("parent_property", "owner")

    def clean(self) -> None:
        total_percentage_owned = self.parent_property.owners.exclude(id=self.pk).aggregate(
            models.Sum("percentage_owned")
        )["percentage_owned__sum"]
        total_percentage_owned = (
            total_percentage_owned + self.percentage_owned if total_percentage_owned else self.percentage_owned
        )
        if total_percentage_owned and total_percentage_owned > 100:
            raise ValidationError("Total percentage owned cannot be greater than 100")
        super().clean()


@receiver(post_save, sender=Property)
def create_late_fee_policy(sender, instance, created, **kwargs):
    if created:
        PropertyLateFeePolicy.objects.create(parent_property=instance, subscription=instance.subscription)


s3 = boto3.resource(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)


@receiver(pre_delete, sender=PropertyAttachment)
def attachment_delete(sender, instance, **kwargs):
    if not settings.DISABLE_S3_DELETE_SIGNAL:
        s3.Object(
            settings.AWS_STORAGE_BUCKET_NAME,
            instance.file,
        ).delete()
        print("deleted")


@receiver(pre_delete, sender=PropertyPhoto)
def photo_delete(sender, instance, **kwargs):
    if not settings.DISABLE_S3_DELETE_SIGNAL:
        s3.Object(
            settings.AWS_STORAGE_BUCKET_NAME,
            instance.image,
        ).delete()
