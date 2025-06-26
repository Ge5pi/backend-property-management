from decimal import Decimal
from typing import List

from django_filters import rest_framework as filters

from .models import PurchaseOrder, ServiceRequest


class ServiceRequestFilter(filters.FilterSet):
    work_order_status = filters.CharFilter(method="filter_work_order_status")
    status = filters.CharFilter()

    class Meta:
        model = ServiceRequest
        fields = ["priority", "order_type"]

    def filter_work_order_status(self, queryset, name, value):
        """
        Filter queryset by work order status.
        """
        return queryset.filter(work_orders__status=value).distinct()


class PurchaseOrderFilter(filters.FilterSet):
    """
    Filter class for :model:`maintenance.PurchaseOrder` model.
    """

    total_greater_than_equal = filters.NumberFilter(method="filter_total_gte")
    total_less_than_equal = filters.NumberFilter(method="filter_total_lte")

    class Meta:
        model = PurchaseOrder
        fields: List[str] = ["vendor"]

    def filter_total_gte(self, queryset, name, value):
        """
        Filter queryset by total greater than or equal to value.
        """
        return queryset.filter(total__gte=Decimal(value))

    def filter_total_lte(self, queryset, name, value):
        """
        Filter queryset by total less than or equal to value.
        """
        return queryset.filter(total__lte=Decimal(value))
