from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from core.mixins import FilterQuerysetByAssociatedSubscriptionMixin
from property.models import UnitType, UnitTypePhoto
from property.serializers import UnitTypePhotoSerializer, UnitTypeSerializer


class UnitTypeViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = UnitType.objects.all().prefetch_related("photos").order_by("-pk")
    serializer_class = UnitTypeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["parent_property"]


class UnitTypePhotoViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = UnitTypePhoto.objects.all().order_by("-pk")
    serializer_class = UnitTypePhotoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["unit_type"]
