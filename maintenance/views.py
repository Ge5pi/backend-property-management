from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.mixins import FilterQuerysetByAssociatedSubscriptionMixin

from .filters import PurchaseOrderFilter, ServiceRequestFilter
from .models import (
    Area,
    AreaItem,
    FixedAsset,
    Inspection,
    Inventory,
    Labor,
    Project,
    ProjectExpense,
    ProjectExpenseAttachment,
    PurchaseOrder,
    PurchaseOrderAttachment,
    PurchaseOrderItem,
    ServiceRequest,
    ServiceRequestAttachment,
    WorkOrder,
)
from .serializers import (
    AreaItemSerializer,
    AreaSerializer,
    FixedAssetBulkCreateSerializer,
    FixedAssetSerializer,
    InspectionSerializer,
    InventorySerializer,
    InventoryUpdateSerializer,
    LaborSerializer,
    ProjectExpenseAttachmentSerializer,
    ProjectExpenseSerializer,
    ProjectSerializer,
    PurchaseOrderAttachmentSerializer,
    PurchaseOrderItemSerializer,
    PurchaseOrderSerializer,
    ServiceRequestAttachmentSerializer,
    ServiceRequestSerializer,
    WorkOrderSerializer,
)


class ServiceRequestViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = (
        ServiceRequest.objects.annotate_slug().annotate_data().select_related("unit").order_by("-pk")  # type: ignore[attr-defined] # noqa: E501
    )
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ["subject", "description", "slug"]
    ordering_fields = ["unit__parent_property__name", "description"]
    filterset_class = ServiceRequestFilter
    serializer_class = ServiceRequestSerializer


class ServiceRequestAttachmentViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = ServiceRequestAttachment.objects.all().order_by("-pk")
    serializer_class = ServiceRequestAttachmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["service_request"]


class WorkOrderViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = (
        WorkOrder.objects.all()
        .annotate_slug()  # type: ignore[attr-defined]
        .order_by("-pk")
        .select_related("vendor_type", "vendor", "assign_to", "service_request")
    )
    serializer_class = WorkOrderSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ["slug", "job_description", "vendor_instructions", "order_type"]
    ordering_fields = ["slug", "job_description", "created_at", "status"]
    filterset_fields = ["status", "service_request"]


class LaborViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    serializer_class = LaborSerializer
    queryset = Labor.objects.all().select_related("work_order").order_by("-pk")
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ["title", "description"]
    filterset_fields = ["work_order"]
    ordering_fields = ["title"]


class InspectionViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = Inspection.objects.all().select_related("unit").order_by("-pk")
    serializer_class = InspectionSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "date"]
    filterset_fields = {"date": ["gte", "lte"], "unit": ["exact"]}


class AreaViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    serializer_class = AreaSerializer
    queryset = Area.objects.all().select_related("inspection").order_by("-pk")
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["name"]
    filterset_fields = ["inspection"]


class AreaItemViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    serializer_class = AreaItemSerializer
    queryset = AreaItem.objects.all().select_related("area").order_by("-pk")
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["area"]


class ProjectViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all().select_related("parent_property").prefetch_related("units").order_by("-pk")
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ["name", "description"]
    filterset_fields = ["status", "parent_property"]
    ordering_fields = ["name", "start_date", "end_date", "status", "budget", "parent_property__name"]


class ProjectExpenseViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = ProjectExpense.objects.all().select_related("project", "assigned_to").order_by("-pk")
    serializer_class = ProjectExpenseSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ["title", "description"]
    filterset_fields = ["project"]
    ordering_fields = ["title", "amount", "created_at"]


class ProjectExpenseAttachmentViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = ProjectExpenseAttachment.objects.all().order_by("-pk")
    serializer_class = ProjectExpenseAttachmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["project_expense"]


class PurchaseOrderViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = (
        PurchaseOrder.objects.annotate_sub_total_and_total()
        .annotate_slug()  # type: ignore[attr-defined]
        .order_by("-pk")
    )
    serializer_class = PurchaseOrderSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ["slug", "vendor__first_name", "vendor__last_name", "description"]
    filterset_class = PurchaseOrderFilter
    ordering_fields = ["slug", "vendor__first_name", "total", "created_at"]


class PurchaseOrderItemViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = PurchaseOrderItem.objects.annotate_total_cost().order_by("-pk")
    serializer_class = PurchaseOrderItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["purchase_order"]


class PurchaseOrderAttachmentViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = PurchaseOrderAttachment.objects.all().order_by("-pk")
    serializer_class = PurchaseOrderAttachmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["purchase_order"]


class InventoryViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = Inventory.objects.all().order_by("pk").prefetch_related("item_type", "location", "vendor")
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = [
        "name",
        "item_type__name",
        "location__name",
        "vendor__first_name",
        "vendor__last_name",
    ]
    filterset_fields = ["item_type", "location", "vendor"]
    ordering_fields = ["name", "quantity", "cost", "item_type__name", "location__name"]

    def get_serializer_class(self):
        if self.action == "update" or self.action == "partial_update":
            return InventoryUpdateSerializer
        else:
            return InventorySerializer

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class FixedAssetViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    serializer_class = FixedAssetSerializer
    queryset = (
        FixedAsset.objects.annotate_slug()  # type: ignore[attr-defined]
        .order_by("-pk")
        .prefetch_related("unit", "inventory_item")
    )
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["slug", "unit__name", "unit__parent_property__name"]
    filterset_fields = ["unit__parent_property", "unit", "status"]
    ordering_fields = [
        "created_at",
        "pk",
        "placed_in_service_date",
        "warranty_expiration_date",
    ]

    def get_serializer_class(self):
        if self.action == "bulk_create":
            return FixedAssetBulkCreateSerializer
        else:
            return FixedAssetSerializer

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ItemsByPurchaseOrderAPIView(FilterQuerysetByAssociatedSubscriptionMixin, generics.ListAPIView):
    queryset = PurchaseOrderItem.objects.annotate_total_cost().order_by("-pk")
    serializer_class = PurchaseOrderItemSerializer

    def get_queryset(self):
        purchase_order_id = self.kwargs.get("purchase_order_id")
        return super().get_queryset().filter(purchase_order=purchase_order_id).order_by("-pk")


class AttachmentsByPurchaseOrderAPIView(FilterQuerysetByAssociatedSubscriptionMixin, generics.ListAPIView):
    queryset = PurchaseOrderAttachment.objects.all()
    serializer_class = PurchaseOrderAttachmentSerializer

    def get_queryset(self):
        purchase_order_id = self.kwargs.get("purchase_order_id")
        return super().get_queryset().filter(purchase_order=purchase_order_id).order_by("-pk")
