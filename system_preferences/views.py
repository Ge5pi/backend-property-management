from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets

from core.mixins import FilterQuerysetByAssociatedSubscriptionMixin

from .models import (
    BusinessInformation,
    ContactCategory,
    InventoryItemType,
    InventoryLocation,
    Label,
    ManagementFee,
    PropertyType,
    Tag,
)
from .serializers import (
    BusinessInformationSerializer,
    ContactCategorySerializer,
    InventoryItemTypeSerializer,
    InventoryLocationSerializer,
    LabelSerializer,
    ManagementFeeSerializer,
    PropertyTypeSerializer,
    TagSerializer,
)


class PropertyTypeViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = PropertyType.objects.annotate_num_records().order_by("-pk")
    serializer_class = PropertyTypeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["created_at", "pk"]


class InventoryItemTypeViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = InventoryItemType.objects.annotate_num_records().order_by("-pk")
    serializer_class = InventoryItemTypeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["created_at", "pk"]


class TagViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = Tag.objects.annotate_num_records().order_by("-pk")
    serializer_class = TagSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["created_at", "pk"]


class LabelViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = Label.objects.annotate_num_records().order_by("-pk")
    serializer_class = LabelSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["created_at", "pk"]


class InventoryLocationViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = InventoryLocation.objects.annotate_num_records().order_by("-pk")
    serializer_class = InventoryLocationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["created_at", "pk"]


class ManagementFeeViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = ManagementFee.objects.all()
    serializer_class = ManagementFeeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ["created_at"]
    search_fields = ["fee", "gl_account"]
    filterset_fields = ["status"]


class BusinessInformationViewSet(
    FilterQuerysetByAssociatedSubscriptionMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = BusinessInformation.objects.all().order_by("-pk")
    serializer_class = BusinessInformationSerializer


class ContactCategoryViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = ContactCategory.objects.annotate_num_records().order_by("-pk")
    serializer_class = ContactCategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["created_at", "pk"]
