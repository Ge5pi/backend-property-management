from django.contrib import admin

from property.models import Unit, UnitPhoto, UnitUpcomingActivity


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("name", "unit_type", "parent_property")
    search_fields = ("name", "unit_type__name", "description")
    list_filter = ("unit_type__parent_property", "unit_type")


@admin.register(UnitUpcomingActivity)
class UnitUpcomingActivityAdmin(admin.ModelAdmin):
    list_display = ("date", "unit", "label")
    search_fields = ("description", "unit__name", "unit__unit_type__name")
    list_filter = ("unit__unit_type__parent_property", "unit__unit_type")


admin.site.register(UnitPhoto)
