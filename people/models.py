from django.contrib.postgres.fields import ArrayField
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField  # type: ignore[import]

from core.models import BaseAttachment, CommonInfoAbstractModel, UpcomingActivityAbstract

from .managers import TenantManager, VendorManager, VendorTypeManager


class Tenant(CommonInfoAbstractModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = PhoneNumberField()
    lease = models.OneToOneField("lease.Lease", related_name="primary_tenant", on_delete=models.CASCADE)
    user = models.ForeignKey("authentication.User", related_name="tenants", on_delete=models.CASCADE)

    objects = TenantManager()

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class TenantUpcomingActivity(UpcomingActivityAbstract, CommonInfoAbstractModel):
    tenant = models.ForeignKey(Tenant, related_name="upcoming_activities", on_delete=models.CASCADE)


class TenantAttachment(BaseAttachment, CommonInfoAbstractModel):
    tenant = models.ForeignKey(Tenant, related_name="attachments", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


class VendorType(CommonInfoAbstractModel):
    SLUG = "vnt"
    name = models.CharField(max_length=100)
    description = models.TextField()

    objects = VendorTypeManager()

    def __str__(self):
        return self.name


class Vendor(CommonInfoAbstractModel):
    SLUG = "vnd"

    class TaxIdentityChoices(models.TextChoices):
        SSN = (
            "SSN",
            "SSN",
        )
        EIN = "EIN", "EIN"

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    use_company_name_as_display_name = models.BooleanField()
    vendor_type = models.ForeignKey(VendorType, related_name="vendors", on_delete=models.CASCADE)
    gl_account = models.CharField(max_length=255)
    personal_contact_numbers = ArrayField(PhoneNumberField())
    business_contact_numbers = ArrayField(PhoneNumberField())
    personal_emails = ArrayField(models.EmailField())
    business_emails = ArrayField(models.EmailField())
    website = models.CharField(max_length=2000)
    # Insurance Details
    insurance_provide_name = models.CharField(max_length=100)
    insurance_policy_number = models.CharField(max_length=100)
    insurance_expiry_date = models.DateField()
    # 1099 Tax filing information
    tax_identity_type = models.CharField(max_length=3, choices=TaxIdentityChoices.choices)
    tax_payer_id = models.CharField(max_length=100)

    objects = VendorManager()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return self.full_name


class VendorAddress(CommonInfoAbstractModel):
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip = models.CharField(max_length=100)
    vendor = models.ForeignKey(Vendor, related_name="addresses", on_delete=models.CASCADE)

    def __str__(self):
        return self.street_address


class VendorAttachment(BaseAttachment, CommonInfoAbstractModel):
    vendor = models.ForeignKey(Vendor, related_name="attachments", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


class Owner(CommonInfoAbstractModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    personal_contact_numbers = ArrayField(PhoneNumberField())
    company_contact_numbers = ArrayField(PhoneNumberField())
    personal_emails = ArrayField(models.EmailField())
    company_emails = ArrayField(models.EmailField())
    # Address
    street_address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    # tax payer details
    tax_payer = models.CharField(max_length=100)
    tax_payer_id = models.CharField(max_length=100)
    # Bank Details
    bank_account_title = models.CharField(max_length=100, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_branch = models.CharField(max_length=100, blank=True, null=True)
    bank_routing_number = models.CharField(max_length=100, blank=True, null=True)
    bank_account_number = models.CharField(max_length=100, blank=True, null=True)
    # Notes
    notes = models.TextField(blank=True, null=True)

    is_company_name_as_tax_payer = models.BooleanField(default=False)
    is_use_as_display_name = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class OwnerUpcomingActivity(UpcomingActivityAbstract, CommonInfoAbstractModel):
    owner = models.ForeignKey(Owner, related_name="upcoming_activities", on_delete=models.CASCADE)
