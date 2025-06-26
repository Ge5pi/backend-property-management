from django_filters import rest_framework as filters

from .models import Charge, Invoice


class InvoiceFilter(filters.FilterSet):
    class Meta:
        model = Invoice
        fields = {
            "parent_property": ["exact"],
            "unit": ["exact"],
            "created_at": ["gte", "lte"],
            "due_date": ["exact"],
            "arrear_of": ["exact"],
            "status": ["exact"],
        }


class ChargeFilter(filters.FilterSet):
    class Meta:
        model = Charge
        fields = {
            "parent_property": ["exact"],
            "unit": ["exact"],
            "status": ["exact"],
            "invoice": ["exact"],
            "created_at": ["lte", "gte"],
        }
