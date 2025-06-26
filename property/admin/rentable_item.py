from django.contrib import admin

from property.models import RentableItem


@admin.register(RentableItem)
class RentableItemAdmin(admin.ModelAdmin):
    list_display = ("name", "parent_property", "amount", "status")
    search_fields = ("name", "parent_property__name")
    list_filter = ("status",)
