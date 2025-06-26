from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField  # type: ignore[import]

from core.models import BaseAttachment, CommonInfoAbstractModel

from .managers import AnnouncementManager, EmailAbstractManager


class Contact(CommonInfoAbstractModel):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        "system_preferences.ContactCategory",
        related_name="contacts",
        on_delete=models.CASCADE,
    )
    primary_contact = PhoneNumberField()
    secondary_contact = PhoneNumberField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    street_address = models.CharField(max_length=255, blank=True, null=True)
    display_to_tenants = models.BooleanField()
    selective = models.BooleanField()

    def __str__(self):
        return self.name


class Note(CommonInfoAbstractModel):
    title = models.CharField(max_length=100)
    description = models.TextField()
    associated_property = models.ForeignKey(
        "property.Property",
        on_delete=models.CASCADE,
        related_name="communication_notes",
    )
    tags = models.ManyToManyField("system_preferences.Tag", related_name="notes", blank=True)

    def __str__(self):
        return self.title


class NoteAttachment(BaseAttachment, CommonInfoAbstractModel):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name="attachments")

    def __str__(self):
        return self.name


class EmailSignature(CommonInfoAbstractModel):
    text = models.TextField()
    image = models.CharField(max_length=2000, blank=True, null=True)

    def __str__(self):
        return self.text


class RecipientType(models.TextChoices):
    INDIVIDUAL = "INDIVIDUAL", "Individual"
    PROPERTY = "PROPERTY", "Property"


class IndividualRecipientType(models.TextChoices):
    TENANT = "TENANT", "Tenant"
    OWNER = "OWNER", "Owner"
    VENDOR = "VENDOR", "Vendor"


class BaseEmailAbstractModel(CommonInfoAbstractModel):
    recipient_type = models.CharField(max_length=10, choices=RecipientType.choices)
    individual_recipient_type = models.CharField(
        max_length=10, choices=IndividualRecipientType.choices, blank=True, null=True
    )

    tenants = models.ManyToManyField("people.Tenant", related_name="%(app_label)s_%(class)s_emails", blank=True)
    owners = models.ManyToManyField("people.Owner", blank=True)
    vendors = models.ManyToManyField("people.Vendor", blank=True)
    units = models.ManyToManyField("property.Unit", blank=True)
    subject = models.CharField(max_length=100)
    body = models.TextField()
    signature = models.ForeignKey(EmailSignature, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self) -> str:
        return self.subject

    class Meta:
        abstract = True

        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(recipient_type=RecipientType.INDIVIDUAL)
                    & models.Q(individual_recipient_type__isnull=False)
                )
                | (models.Q(recipient_type=RecipientType.PROPERTY) & models.Q(individual_recipient_type__isnull=True)),
                name="%(class)s_individual_recipient_type_required_for_indiv_recip",
                violation_error_message="Individual recipient type is required for individual recipient type",
            ),
        ]

    objects = EmailAbstractManager()


class EmailTemplate(BaseEmailAbstractModel):
    pass


class Email(BaseEmailAbstractModel):
    recipient_emails = ArrayField(
        models.EmailField(),
        blank=True,
        null=True,
        help_text="This field is populated automatically",
    )
    template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.SET_NULL,
        related_name="emails",
        blank=True,
        null=True,
    )


class EmailAttachment(BaseAttachment, CommonInfoAbstractModel):
    email = models.ForeignKey(Email, related_name="attachments", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Announcement(CommonInfoAbstractModel):
    class SelectionChoices(models.TextChoices):
        ALL_PROPERTIES_AND_UNITS = "APAU", "All Properties & Units"
        SELECTIVE_PROPERTIES_AND_ALL_UNITS = (
            "SPAU",
            "Selective Properties and All Units",
        )
        SELECTIVE_PROPERTIES_AND_UNITS = "SPSU", "Selective Properties and Units"
        ALL_PROPERTIES_AND_SELECTIVE_UNITS = (
            "APSU",
            "All Properties and Selective Units",
        )

    title = models.CharField(max_length=100)
    body = models.TextField()
    selection = models.CharField(
        max_length=4,
        choices=SelectionChoices.choices,
        default=SelectionChoices.SELECTIVE_PROPERTIES_AND_UNITS,
    )
    send_by_email = models.BooleanField()
    display_on_tenant_portal = models.BooleanField()
    display_date = models.DateField()
    expiry_date = models.DateField()
    properties = models.ManyToManyField("property.Property", blank=True)
    units = models.ManyToManyField("property.Unit", blank=True)

    objects = AnnouncementManager()

    def __str__(self):
        return self.title


class AnnouncementAttachment(BaseAttachment, CommonInfoAbstractModel):
    announcement = models.ForeignKey(Announcement, related_name="attachments", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


@receiver(m2m_changed, sender=Email.tenants.through)
@receiver(m2m_changed, sender=Email.owners.through)
@receiver(m2m_changed, sender=Email.vendors.through)
@receiver(m2m_changed, sender=Email.units.through)
def populate_recipient_emails(sender, instance, **kwargs):
    if kwargs["action"] == "post_add":
        instance.recipient_emails = Email.objects.get_recipient_emails(instance)
        instance.save()
