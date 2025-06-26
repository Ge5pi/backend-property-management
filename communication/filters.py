from django_filters import rest_framework as filters

from .models import Announcement


class AnnouncementFilter(filters.FilterSet):
    """
    Filter class for :model:`maintenance.PurchaseOrder` model.
    """

    status = filters.CharFilter(method="filter_by_status")

    class Meta:
        model = Announcement
        fields = {
            "units": ["exact"],
            "properties": ["exact"],
        }

    def filter_by_status(self, queryset, name, value):
        """
        Filter queryset by total less than or equal to value.
        """
        return queryset.annotate_status().filter(status=value)
