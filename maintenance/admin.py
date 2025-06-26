from django.contrib import admin

from .models import (
    Area,
    AreaItem,
    FixedAsset,
    Inspection,
    Inventory,
    Labor,
    Project,
    PurchaseOrder,
    PurchaseOrderItem,
    ServiceRequest,
    WorkOrder,
)


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = [
        "unit",
        "permission_to_enter",
        "priority",
    ]
    search_fields = ["unit", "description"]
    list_filter = [
        "priority",
    ]


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = [
        "service_request",
        "order_type",
        "status",
        "is_recurring",
        "cycle",
        "vendor",
        "assign_to",
        "created_by",
    ]
    search_fields = ["job_description", "vendor_instructions", "vendor_trade"]
    list_filter = ["email_vendor", "cycle", "is_recurring", "status", "order_type"]


@admin.register(Labor)
class LaborAdmin(admin.ModelAdmin):
    list_display = ["title", "date", "hours"]
    search_fields = ["title", "description"]


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ["name", "date", "unit"]
    search_fields = ["name", "unit__name"]


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(AreaItem)
class AreaItemAdmin(admin.ModelAdmin):
    list_display = ["name", "condition"]
    search_fields = ["name"]
    list_filter = ["condition"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "parent_property", "start_date", "end_date"]
    search_fields = ["name", "parent_property__name"]


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ["description"]
    search_fields = ["description"]


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ["purchase_order", "inventory_item", "quantity", "cost"]
    search_fields = ["inventory_item"]


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ["name", "cost", "item_type"]
    list_filter = ["item_type", "location"]
    search_fields = ["name"]


@admin.register(FixedAsset)
class FixedAssetAdmin(admin.ModelAdmin):
    list_display = ("unit", "cost", "inventory_item", "quantity")
    search_fields = ("unit", "inventory_item")
    list_filter = ("status",)
