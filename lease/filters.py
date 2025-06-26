from datetime import timedelta

from django.db.models import DurationField, ExpressionWrapper, F, Q
from django.utils import timezone
from django_filters import rest_framework as filters

from .models import Lease


class LeaseFilter(filters.FilterSet):
    remaining_days_less_than = filters.NumberFilter(method="filter_remaining_days_lte")

    class Meta:
        model = Lease
        fields = ["unit", "status", "unit__parent_property"]

    def filter_remaining_days_lte(self, queryset, name, value):
        """
        Filter queryset by remaining days less than or equal to value.
        """
        qs = queryset.annotate(
            days_left_to_expire=ExpressionWrapper(F("end_date") - timezone.now().date(), output_field=DurationField())
        )
        return qs.filter(
            Q(days_left_to_expire__lte=timedelta(days=int(value))) & Q(days_left_to_expire__gte=timedelta(days=0))
        )
