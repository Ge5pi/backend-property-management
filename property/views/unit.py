from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from core.mixins import FilterQuerysetByAssociatedSubscriptionMixin
from property.filters import UnitFilter, UnitUpcomingActivityFilter
from property.models import Unit, UnitPhoto, UnitUpcomingActivity
from property.serializers import (
    UnitListSerializer,
    UnitPhotoSerializer,
    UnitSerializer,
    UnitUpcomingActivitySerializer,
)


class UnitViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = (
        Unit.objects.select_related("unit_type")
        .prefetch_related("leases", "photos")
        .annotate_slug()  # type: ignore[attr-defined]
        .annotate_data()  # type: ignore[attr-defined]
        .order_by("-pk")
    )
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = UnitFilter
    search_fields = ["name", "address", "slug"]

    def get_serializer_class(self):
        if self.action == "list":
            return UnitListSerializer
        else:
            return UnitSerializer


class UnitUpcomingActivityViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = UnitUpcomingActivity.objects.select_related("label", "assign_to", "unit").order_by("-pk")
    serializer_class = UnitUpcomingActivitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UnitUpcomingActivityFilter


class UnitPhotoViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = UnitPhoto.objects.all().order_by("-pk")
    serializer_class = UnitPhotoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["unit"]
