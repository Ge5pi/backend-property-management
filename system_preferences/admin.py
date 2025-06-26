from django.contrib import admin

from .models import (
    BusinessInformation,
    ContactCategory,
    InventoryItemType,
    InventoryLocation,
    Label,
    ManagementFee,
    PropertyType,
    Tag,
)


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(InventoryItemType)
class InventoryItemTypeAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(InventoryLocation)
class InventoryLocationAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(ManagementFee)
class ManagementFeeAdmin(admin.ModelAdmin):
    list_display = ["fee", "fee_type", "gl_account", "status", "created_at"]
    search_fields = ["gl_account"]
    list_filter = ["status", "fee_type"]
    readonly_fields = ["created_at", "status"]


@admin.register(ContactCategory)
class ContactCategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(BusinessInformation)
class BusinessInformationAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
