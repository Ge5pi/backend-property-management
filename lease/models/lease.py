from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField  # type: ignore[import]

from core.models import CommonInfoAbstractModel
from people.models import Tenant

from ..managers import LeaseManager

User = get_user_model()


class LeaseTemplate(CommonInfoAbstractModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    # policies & procedures
    rules_and_policies = ArrayField(models.CharField(max_length=300), blank=True, null=True)

    # Responsibilities
    condition_of_premises = ArrayField(models.CharField(max_length=300), blank=True, null=True)

    right_of_inspection = models.BooleanField(default=True)
    conditions_of_moving_out = ArrayField(models.CharField(max_length=300), blank=True, null=True)

    # general
    releasing_policies = ArrayField(models.CharField(max_length=300), blank=True, null=True)

    final_statement = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name


class Lease(CommonInfoAbstractModel):
    class LeaseStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        CLOSED = "CLOSED", "Closed"

    class LeaseType(models.TextChoices):
        FIXED = "FIXED", "Fixed"
        AT_WILL = "AT_WILL", "At Will"

    class RentCycleChoices(models.TextChoices):
        WEEKLY = "WEEKLY", "Weekly"
        MONTHLY = "MONTHLY", "Monthly"
        QUARTERLY = "QUARTERLY", "Quarterly"
        SIX_MONTHS = "SIX_MONTHS", "Six Months"
        YEARLY = "YEARLY", "Yearly"

    rental_application = models.ForeignKey("RentalApplication", related_name="leases", on_delete=models.CASCADE)
    lease_type = models.CharField(max_length=100, choices=LeaseType.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    lease_template = models.ForeignKey(
        "LeaseTemplate",
        related_name="leases",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    # Rent Details
    rent_cycle = models.CharField(max_length=12, choices=RentCycleChoices.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    gl_account = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True, default="rent")
    # Security Deposit
    due_date = models.DateField()

    status = models.CharField(max_length=100, choices=LeaseStatus.choices, default=LeaseStatus.ACTIVE)
    closed_on = models.DateField(blank=True, null=True)
    unit = models.ForeignKey("property.Unit", related_name="leases", on_delete=models.CASCADE)

    # Lease Template
    # policies & procedures
    rules_and_policies = ArrayField(models.CharField(max_length=100), blank=True, null=True)

    # Responsibilities
    condition_of_premises = ArrayField(models.CharField(max_length=100), blank=True, null=True)

    right_of_inspection = models.BooleanField(blank=True, null=True)
    conditions_of_moving_out = ArrayField(models.CharField(max_length=100), blank=True, null=True)

    # general
    releasing_policies = ArrayField(models.CharField(max_length=100), blank=True, null=True)

    final_statement = models.TextField(blank=True, null=True)

    objects = LeaseManager()

    def __str__(self) -> str:
        return str(self.rental_application.applicant)

    def close_lease(self):
        if self.status == self.LeaseStatus.ACTIVE:
            self.status = self.LeaseStatus.CLOSED
            self.closed_on = timezone.now()
            self.save()

    def save(self, *args, **kwargs):
        self.unit = self.rental_application.applicant.unit
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["status", "unit"],
                condition=Q(status="ACTIVE"),
                name="one_active_lease_for_unit",
                violation_error_message="Only one active lease can exist against a unit.",
            )
        ]


class SecondaryTenant(CommonInfoAbstractModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone_number = PhoneNumberField()
    birthday = models.DateField()
    tax_payer_id = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    lease = models.ForeignKey("Lease", related_name="secondary_tenants", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


@receiver(post_save, sender=Lease)
def create_lease_tenant(sender, instance, created, **kwargs):
    if created:
        email = instance.rental_application.applicant.email
        first_name = instance.rental_application.applicant.first_name
        last_name = instance.rental_application.applicant.last_name
        phone_number = instance.rental_application.applicant.phone_number

        user, created = User.objects.get_or_create(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            mobile_number=phone_number,
            associated_subscription=instance.subscription,
        )

        try:
            tenant_group = Group.objects.get(name=settings.TENANT_GROUP_NAME)
            user.groups.add(tenant_group)
        except ObjectDoesNotExist:
            pass

        if created:
            User.objects.set_random_password(user)
        Tenant.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            lease=instance,
            user=user,
            subscription=instance.subscription,
        )


@receiver(post_save, sender=Lease)
def create_lease_template_data(sender, instance, created, **kwargs):
    if created:
        template = instance.unit.parent_property.default_lease_template
        if template is not None:
            instance.lease_template = template
            instance.rules_and_policies = template.rules_and_policies
            instance.condition_of_premises = template.condition_of_premises
            instance.right_of_inspection = template.right_of_inspection
            instance.conditions_of_moving_out = template.conditions_of_moving_out
            instance.releasing_policies = template.releasing_policies
            instance.final_statement = template.final_statement

        instance.save()
