from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AreaItemViewSet,
    AreaViewSet,
    AttachmentsByPurchaseOrderAPIView,
    FixedAssetViewSet,
    InspectionViewSet,
    InventoryViewSet,
    ItemsByPurchaseOrderAPIView,
    LaborViewSet,
    ProjectExpenseAttachmentViewSet,
    ProjectExpenseViewSet,
    ProjectViewSet,
    PurchaseOrderAttachmentViewSet,
    PurchaseOrderItemViewSet,
    PurchaseOrderViewSet,
    ServiceRequestAttachmentViewSet,
    ServiceRequestViewSet,
    WorkOrderViewSet,
)

app_name = "maintenance"

router = DefaultRouter()
router.register("service-requests", ServiceRequestViewSet, basename="service_requests")
router.register("service-request-attachments", ServiceRequestAttachmentViewSet, basename="service_request_attachments")
router.register("work-orders", WorkOrderViewSet, "work_orders")
router.register("inspections", InspectionViewSet, basename="inspection")
router.register("projects", ProjectViewSet, basename="project")
router.register("purchase-orders", PurchaseOrderViewSet, basename="purchase_orders")
router.register("purchase-orders-items", PurchaseOrderItemViewSet, basename="purchase_order_items")
router.register("purchase-orders-attachments", PurchaseOrderAttachmentViewSet, basename="purchase_order_attachments")
router.register("fixed-assets", FixedAssetViewSet, basename="fixed_assets")
router.register("inventory", InventoryViewSet, basename="inventory")
router.register("fixed-assets", FixedAssetViewSet, basename="fixed-assets")
router.register("area", AreaViewSet, basename="area")
router.register("area-items", AreaItemViewSet, basename="area_item")
router.register("labors", LaborViewSet, basename="labor")
router.register("project-expenses", ProjectExpenseViewSet, basename="project_expense")
router.register("project-expense-attachments", ProjectExpenseAttachmentViewSet, basename="project_expense_attachments")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "purchase-orders/<int:purchase_order_id>/items/",
        ItemsByPurchaseOrderAPIView.as_view(),
        name="items-by-purchase-order",
    ),
    path(
        "purchase-orders/<int:purchase_order_id>/attachments/",
        AttachmentsByPurchaseOrderAPIView.as_view(),
        name="attachments-by-purchase-order",
    ),
]
