from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField  # type: ignore[import]

from core.models import BaseAttachment, CommonInfoAbstractModel

from ..managers import RentalApplicationManager


class RentalApplicationTemplate(CommonInfoAbstractModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    general_info = models.BooleanField(default=True)
    personal_details = models.BooleanField(default=True)
    rental_history = models.BooleanField(default=True)
    financial_info = models.BooleanField(default=True)
    dependents_info = models.BooleanField(default=True)
    other_info = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class Applicant(CommonInfoAbstractModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    allow_email_for_rental_application = models.BooleanField(default=False)
    phone_number = PhoneNumberField()
    unit = models.ForeignKey("property.Unit", related_name="applicants", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class RentalApplication(CommonInfoAbstractModel):
    SLUG = "rta"

    class ApplicantTypeChoices(models.TextChoices):
        FINANCIALlY_INDEPENDENT = "FINANCIALlY_INDEPENDENT", "Financially Independent"
        DEPENDENT = "DEPENDENT", "Dependent"

    class RentalApplicationStatusChoices(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        ON_HOLD_OR_WAITING = "ON_HOLD_OR_WAITING", "On Hold/Waiting"

    applicant = models.OneToOneField(Applicant, related_name="rental_application", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=RentalApplicationStatusChoices.choices,
        default=RentalApplicationStatusChoices.DRAFT,
    )
    desired_move_in_date = models.DateField(blank=True, null=True)
    legal_first_name = models.CharField(max_length=100, blank=True, null=True)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    legal_last_name = models.CharField(max_length=100, blank=True, null=True)
    application_type = models.CharField(max_length=100, choices=ApplicantTypeChoices.choices, blank=True, null=True)
    phone_number = ArrayField(PhoneNumberField(), blank=True, null=True)
    emails = ArrayField(models.EmailField(), blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    # Personal Information
    birthday = models.DateField(blank=True, null=True)
    ssn_or_tin = models.CharField(max_length=100, blank=True, null=True)
    driving_license_number = models.CharField(max_length=100, blank=True, null=True)
    # Employment Details
    employer_name = models.CharField(max_length=100, blank=True, null=True)
    employer_address = models.TextField(blank=True, null=True)
    employer_address_2 = models.TextField(blank=True, null=True)
    employer_phone_number = models.CharField(max_length=100, blank=True, null=True)
    employment_city = models.CharField(max_length=100, blank=True, null=True)
    employment_zip_code = models.CharField(max_length=100, blank=True, null=True)
    employment_country = models.CharField(max_length=100, blank=True, null=True)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    position_held = models.CharField(max_length=100, blank=True, null=True)
    years_worked = models.IntegerField(blank=True, null=True)
    supervisor_name = models.CharField(max_length=100, blank=True, null=True)
    supervisor_phone_number = models.CharField(max_length=100, blank=True, null=True)
    supervisor_email = models.EmailField(blank=True, null=True)
    supervisor_title = models.CharField(max_length=100, blank=True, null=True)

    # Questions
    is_defendant_in_any_lawsuit = models.BooleanField(
        default=False,
        help_text="""
        Have you ever been a defendant in unlawful detainer or failed to perform any obligation of a rental lease?
        """,
    )
    is_convicted = models.BooleanField(default=False, help_text="Have you ever been convicted of crime?")
    have_filed_case_against_landlord = models.BooleanField(
        default=False, help_text="Have you ever filed case against a landlord?"
    )
    is_smoker = models.BooleanField(default=False, help_text="Are you or any of your dependents a smoker?")

    # Rental Application Template For Rendering Fields
    general_info = models.BooleanField(default=False)
    personal_details = models.BooleanField(default=False)
    rental_history = models.BooleanField(default=False)
    financial_info = models.BooleanField(default=False)
    dependents_info = models.BooleanField(default=False)
    other_info = models.BooleanField(default=False)

    # Form Fill Tracking
    is_general_info_filled = models.BooleanField(default=False)
    is_personal_details_filled = models.BooleanField(default=False)
    is_rental_history_filled = models.BooleanField(default=False)
    is_financial_info_filled = models.BooleanField(default=False)
    is_dependents_filled = models.BooleanField(default=False)
    is_other_info_filled = models.BooleanField(default=False)

    objects = RentalApplicationManager()

    def __str__(self) -> str:
        return f"{self.legal_first_name} {self.legal_last_name}"


class RentalApplicationEmergencyContact(CommonInfoAbstractModel):
    name = models.CharField(max_length=100)
    phone_number = PhoneNumberField()
    relationship = models.CharField(max_length=100)
    address = models.TextField()
    rental_application = models.ForeignKey(
        RentalApplication, related_name="emergency_contacts", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return self.name


class RentalApplicationResidentialHistory(CommonInfoAbstractModel):
    current_address = models.TextField()
    current_address_2 = models.TextField(blank=True, null=True)
    current_city = models.CharField(max_length=100, blank=True, null=True)
    current_zip_code = models.CharField(max_length=100, blank=True, null=True)
    current_country = models.CharField(max_length=100)
    resident_from = models.DateField(blank=True, null=True)
    resident_to = models.DateField(blank=True, null=True)
    landlord_name = models.CharField(max_length=100, blank=True, null=True)
    landlord_phone_number = PhoneNumberField(blank=True, null=True)
    landlord_email = models.EmailField(blank=True, null=True)
    reason_of_leaving = models.TextField(blank=True, null=True)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    current_state = models.CharField(max_length=100, blank=True, null=True)
    rental_application = models.ForeignKey(
        "RentalApplication",
        related_name="residential_history",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.current_address[:25]}..."


class RentalApplicationFinancialInformation(CommonInfoAbstractModel):
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=100)
    bank = models.CharField(max_length=100)
    account_number = models.CharField(max_length=100)

    rental_application = models.ForeignKey(
        "RentalApplication",
        related_name="financial_information",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.name}"


class RentalApplicationAdditionalIncome(CommonInfoAbstractModel):
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2)
    source_of_income = models.CharField(max_length=100)
    rental_application = models.ForeignKey(
        "RentalApplication",
        related_name="additional_income",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.source_of_income}"


class RentalApplicationDependent(CommonInfoAbstractModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birthday = models.DateField()
    relationship = models.CharField(max_length=100)
    rental_application = models.ForeignKey(
        "RentalApplication",
        related_name="dependents",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class RentalApplicationPets(CommonInfoAbstractModel):
    name = models.CharField(max_length=100)
    pet_type = models.CharField(max_length=100)
    weight = models.FloatField(blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    rental_application = models.ForeignKey(
        "RentalApplication",
        related_name="pets",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        verbose_name_plural = "RentalApplicationPets"


class RentalApplicationAttachment(BaseAttachment, CommonInfoAbstractModel):
    rental_application = models.ForeignKey(
        RentalApplication,
        on_delete=models.CASCADE,
        related_name="attachments",
    )

    class Meta:
        verbose_name_plural = "Attachments"

    def __str__(self):
        return self.name


@receiver(post_save, sender=Applicant)
def create_rental_application_on_application_save(sender, instance, created, *args, **kwargs):
    if created:
        rental_application = RentalApplication(applicant=instance, subscription=instance.subscription)
        template = instance.unit.parent_property.rental_application_template
        if template is not None:
            rental_application.general_info = template.general_info
            rental_application.personal_details = template.personal_details
            rental_application.rental_history = template.rental_history
            rental_application.financial_info = template.financial_info
            rental_application.dependents_info = template.dependents_info
            rental_application.other_info = template.other_info

        rental_application.save()
