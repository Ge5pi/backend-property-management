from django.contrib import admin

from property.models import UnitType, UnitTypePhoto


@admin.register(UnitType)
class UnitTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "parent_property")
    search_fields = ("name", "parent_property__name")


@admin.register(UnitTypePhoto)
class UnitTypePhotoAdmin(admin.ModelAdmin):
    list_display = ("unit_type", "image")
