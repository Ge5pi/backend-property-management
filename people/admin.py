from django.contrib import admin

from .models import (
    Owner,
    OwnerUpcomingActivity,
    Tenant,
    TenantAttachment,
    TenantUpcomingActivity,
    Vendor,
    VendorAddress,
    VendorAttachment,
    VendorType,
)


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "email", "phone_number", "lease", "user"]
    search_fields = ["first_name", "last_name", "email", "phone_number", "lease"]


@admin.register(TenantUpcomingActivity)
class TenantUpcomingActivityModelAdmin(admin.ModelAdmin):
    list_display = ["label", "assign_to", "status", "tenant"]
    search_fields = ["description"]
    list_filter = ["status"]


@admin.register(TenantAttachment)
class TenantAttachmentAdmin(admin.ModelAdmin):
    list_display = ["name", "created_by", "file_type", "updated_at"]


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "company_name"]
    search_fields = ["first_name", "last_name", "company_name"]


@admin.register(OwnerUpcomingActivity)
class OwnerUpcomingActivityModelAdmin(admin.ModelAdmin):
    list_display = ["label", "assign_to", "status", "owner"]
    search_fields = ["description"]
    list_filter = ["status"]


admin.site.register(Vendor)
admin.site.register(VendorType)
admin.site.register(VendorAttachment)
admin.site.register(VendorAddress)
