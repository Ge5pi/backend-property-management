from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from core.mixins import FilterQuerysetByAssociatedSubscriptionMixin
from property.models import RentableItem
from property.serializers import RentableItemSerializer


class RentableItemViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = RentableItem.objects.all().select_related("tenant").order_by("-pk")
    serializer_class = RentableItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["parent_property"]
