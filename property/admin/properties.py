from django.contrib import admin

from property.models import (
    Property,
    PropertyAttachment,
    PropertyLateFeePolicy,
    PropertyOwner,
    PropertyPhoto,
    PropertyUpcomingActivity,
    PropertyUtilityBilling,
)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "property_type")
    list_filter = ("property_type",)
    search_fields = ("name", "address")


@admin.register(PropertyUpcomingActivity)
class UpcomingActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "label", "assign_to", "status", "parent_property")
    list_filter = ("label", "assign_to", "status", "parent_property")
    search_fields = (
        "description",
        "label__name",
        "assign_to__username",
        "parent_property__name",
    )


@admin.register(PropertyUtilityBilling)
class UtilityBillingAdmin(admin.ModelAdmin):
    list_display = (
        "utility",
        "vendor",
        "owner_contribution_percentage",
        "tenant_contribution_percentage",
    )
    search_fields = ("utility", "vendor")


@admin.register(PropertyLateFeePolicy)
class LateFeePolicyAdmin(admin.ModelAdmin):
    list_display = (
        "start_date",
        "end_date",
        "base_amount_fee",
        "grace_period",
    )
    search_fields = ("parent_property__name",)


@admin.register(PropertyAttachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "file_type", "updated_at")
    search_fields = ("name", "created_by", "file_type")
    list_filter = ("file_type",)


@admin.register(PropertyPhoto)
class PhotoAdmin(admin.ModelAdmin):
    list_display = (
        "parent_property",
        "is_cover",
    )
    search_fields = ("is_cover", "parent_property__name")
    list_filter = ("is_cover",)


@admin.register(PropertyOwner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = (
        "owner",
        "percentage_owned",
        "parent_property",
        "ownership_start_date",
    )
    search_fields = ("owner__username", "parent_property__name")
