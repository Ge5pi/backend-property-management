from django_filters import rest_framework as filters

from core.filters import UpcomingActivityFilter

from .models import Property, PropertyUpcomingActivity, Unit, UnitUpcomingActivity


class PropertyFilter(filters.FilterSet):
    is_occupied = filters.BooleanFilter()

    class Meta:
        model = Property
        fields = ["property_type"]


class PropertyUpcomingActivityFilter(UpcomingActivityFilter):
    class Meta:
        model = PropertyUpcomingActivity
        fields = ["parent_property"]


class UnitUpcomingActivityFilter(UpcomingActivityFilter):
    class Meta:
        model = UnitUpcomingActivity
        fields = ["unit"]


class UnitFilter(filters.FilterSet):
    is_occupied = filters.BooleanFilter()

    class Meta:
        model = Unit
        fields = ["parent_property", "unit_type"]
