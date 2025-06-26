from django.contrib import admin

from .models import (
    Applicant,
    Lease,
    LeaseTemplate,
    RentalApplication,
    RentalApplicationAdditionalIncome,
    RentalApplicationDependent,
    RentalApplicationEmergencyContact,
    RentalApplicationFinancialInformation,
    RentalApplicationPets,
    RentalApplicationResidentialHistory,
    RentalApplicationTemplate,
    SecondaryTenant,
)


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone_number", "unit")
    search_fields = ("first_name", "last_name", "email", "phone_number")


@admin.register(RentalApplication)
class RentalApplicationAdmin(admin.ModelAdmin):
    list_display = ("applicant", "status")
    search_fields = (
        "applicant__first_name",
        "applicant__last_name",
        "applicant__email",
    )
    list_filter = ("status",)


@admin.register(RentalApplicationResidentialHistory)
class RentalApplicationResidentialHistoryAdmin(admin.ModelAdmin):
    list_display = ("current_address", "rental_application")
    search_fields = (
        "current_address",
        "rental_application__applicant__first_name",
        "rental_application__applicant__last_name",
        "rental_application__applicant__email",
    )
    list_filter = ("rental_application__status",)


@admin.register(RentalApplicationFinancialInformation)
class RentalApplicationFinancialInformationAdmin(admin.ModelAdmin):
    list_display = ("name", "rental_application")
    search_fields = (
        "name",
        "rental_application__applicant__first_name",
        "rental_application__applicant__last_name",
        "rental_application__applicant__email",
    )
    list_filter = ("rental_application__status",)


@admin.register(RentalApplicationAdditionalIncome)
class RentalApplicationAdditionalIncomeAdmin(admin.ModelAdmin):
    list_display = ("source_of_income", "monthly_income", "rental_application")
    search_fields = (
        "name",
        "rental_application__applicant__first_name",
        "rental_application__applicant__last_name",
        "rental_application__applicant__email",
    )
    list_filter = ("rental_application__status",)


@admin.register(RentalApplicationDependent)
class RentalApplicationDependentAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "rental_application")
    search_fields = (
        "name",
        "rental_application__applicant__first_name",
        "rental_application__applicant__last_name",
        "rental_application__applicant__email",
    )
    list_filter = ("rental_application__status",)


@admin.register(RentalApplicationPets)
class RentalApplicationPetsAdmin(admin.ModelAdmin):
    list_display = ("name", "rental_application")
    search_fields = (
        "name",
        "rental_application__applicant__first_name",
        "rental_application__applicant__last_name",
        "rental_application__applicant__email",
    )
    list_filter = ("rental_application__status",)


@admin.register(RentalApplicationTemplate)
class RentalApplicationTemplateAdmin(admin.ModelAdmin):
    pass


@admin.register(LeaseTemplate)
class LeaseTemplateAdmin(admin.ModelAdmin):
    pass


@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ("rental_application", "status")
    search_fields = (
        "rental_application__applicant__first_name",
        "rental_application__applicant__last_name",
        "rental_application__applicant__email",
    )
    list_filter = ("status",)


@admin.register(SecondaryTenant)
class SecondaryTenantAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "phone_number", "lease")
    search_fields = ("first_name", "last_name", "phone_number")


@admin.register(RentalApplicationEmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ("name", "rental_application", "phone_number")
    search_fields = ("name", "address")
