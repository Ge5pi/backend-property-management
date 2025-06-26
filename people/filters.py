from django_filters import rest_framework as filters

from core.filters import UpcomingActivityFilter

from .models import OwnerUpcomingActivity, Tenant, TenantUpcomingActivity


class TenantFilter(filters.FilterSet):
    status = filters.CharFilter(method="filter_by_status")
    unit_id = filters.CharFilter(method="filter_by_unit")
    property_id = filters.CharFilter(method="filter_by_property")

    class Meta:
        model = Tenant
        fields = ["unit_id", "property_id", "status"]

    def filter_by_status(self, queryset, name, value):
        """
        Filter queryset by total less than or equal to value.
        """
        return queryset.filter(status=value)

    def filter_by_unit(self, queryset, name, value):
        return queryset.filter(lease__unit=value)

    def filter_by_property(self, queryset, name, value):
        return queryset.filter(lease__unit__parent_property=value)


class OwnerUpcomingActivityFilter(UpcomingActivityFilter):
    class Meta:
        model = OwnerUpcomingActivity
        fields = ["owner"]


class TenantUpcomingActivityFilter(UpcomingActivityFilter):
    class Meta:
        model = TenantUpcomingActivity
        fields = ["tenant"]
