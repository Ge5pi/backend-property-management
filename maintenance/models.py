from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from core.models import BaseAttachment, CommonInfoAbstractModel

from .managers import (
    FixedAssetManager,
    PurchaseOrderItemManager,
    PurchaseOrderManager,
    ServiceRequestManager,
    WorkOrderManager,
)


class ChargeType(models.TextChoices):
    PERCENT = "PERCENT", "Percent"
    FLAT = "FLAT", "Flat"


class OrderTypeChoices(models.TextChoices):
    INTERNAL = "INTERNAL", "Internal"
    RESIDENT = "RESIDENT", "Resident"
    UNIT_TURN = "UNIT_TURN", "Unit Turn"


class ServiceRequest(CommonInfoAbstractModel):
    SLUG = "srq"

    class PriorityChoices(models.TextChoices):
        URGENT = "URGENT", "Urgent"
        NORMAL = "NORMAL", "Normal"
        LOW = "LOW", "Low"

    unit = models.ForeignKey(
        "property.Unit",
        related_name="service_requests",
        on_delete=models.CASCADE,
    )
    order_type = models.CharField(max_length=9, choices=OrderTypeChoices.choices)
    permission_to_enter = models.BooleanField(default=False)
    additional_information_for_entry = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=6, choices=PriorityChoices.choices)
    subject = models.CharField(max_length=255)
    description = models.TextField()

    objects = ServiceRequestManager()

    def __str__(self):
        return self.subject


class ServiceRequestAttachment(BaseAttachment, CommonInfoAbstractModel):
    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="attachments",
    )

    def __str__(self):
        return self.name


class WorkOrder(CommonInfoAbstractModel):
    SLUG = "wko"

    class CycleChoices(models.TextChoices):
        DAILY = "DAILY", "Daily"
        WEEKLY = "WEEKLY", "Weekly"
        MONTHLY = "MONTHLY", "Monthly"
        YEARLY = (
            "YEARLY",
            "Yearly",
        )
        SIX_MONTHS = "SIX_MONTHS", "Six Months"

    class StatusChoices(models.TextChoices):
        OPEN = "OPEN", "Open"
        ASSIGNED = "ASSIGNED", "Assigned"
        UNASSIGNED = "UNASSIGNED", "Un-Assigned"
        COMPLETED = "COMPLETED", "Completed"

    is_recurring = models.BooleanField(default=False)
    cycle = models.CharField(max_length=10, choices=CycleChoices.choices, blank=True, null=True)
    status = models.CharField(max_length=12, choices=StatusChoices.choices, default=StatusChoices.OPEN)
    order_type = models.CharField(max_length=9, choices=OrderTypeChoices.choices)
    job_description = models.TextField(blank=True, null=True)
    vendor_instructions = models.TextField(blank=True, null=True)
    vendor_trade = models.CharField(max_length=255, blank=True, null=True)
    vendor_type = models.ForeignKey(
        "people.VendorType",
        related_name="work_orders",
        on_delete=models.CASCADE,
    )
    vendor = models.ForeignKey(
        "people.Vendor",
        related_name="work_orders",
        on_delete=models.CASCADE,
    )
    email_vendor = models.BooleanField()
    request_receipt = models.BooleanField()
    assign_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="assigned_work_orders",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    owner_approved = models.BooleanField()
    follow_up_date = models.DateField()
    service_request = models.ForeignKey(ServiceRequest, related_name="work_orders", on_delete=models.CASCADE)

    objects = WorkOrderManager()

    def __str__(self) -> str:
        return self.service_request.unit.name


class Labor(CommonInfoAbstractModel):
    title = models.CharField(max_length=255)
    date = models.DateField()
    hours = models.IntegerField()
    description = models.TextField()
    work_order = models.ForeignKey(WorkOrder, related_name="labors", on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Inspection(CommonInfoAbstractModel):
    name = models.CharField(max_length=255)
    date = models.DateField()
    unit = models.ForeignKey(
        "property.Unit",
        related_name="inspections",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Area(CommonInfoAbstractModel):
    name = models.CharField(max_length=255)
    inspection = models.ForeignKey(Inspection, related_name="areas", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


class AreaItem(CommonInfoAbstractModel):
    class ConditionChoices(models.TextChoices):
        OKAY = "OKAY", "Okay"
        NOT_OKAY = "NOT_OKAY", "Not Okay"

    name = models.CharField(max_length=255)
    condition = models.CharField(max_length=8, choices=ConditionChoices.choices)
    area = models.ForeignKey(Area, related_name="items", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


class Project(CommonInfoAbstractModel):
    class StatusChoices(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"

    name = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=12, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    parent_property = models.ForeignKey("property.Property", related_name="projects", on_delete=models.CASCADE)
    units = models.ManyToManyField("property.Unit", related_name="projects", blank=True)
    select_all_units = models.BooleanField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    gl_account = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name


class ProjectExpense(CommonInfoAbstractModel):
    title = models.CharField(max_length=100)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="project_expenses",
        on_delete=models.CASCADE,
    )
    project = models.ForeignKey(Project, related_name="expenses", on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class ProjectExpenseAttachment(BaseAttachment, CommonInfoAbstractModel):
    project_expense = models.ForeignKey(
        ProjectExpense,
        on_delete=models.CASCADE,
        related_name="attachments",
    )

    def __str__(self):
        return self.name


class PurchaseOrder(CommonInfoAbstractModel):
    SLUG = "po"
    vendor = models.ForeignKey(
        "people.Vendor",
        related_name="purchase_orders",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    description = models.TextField()
    required_by_date = models.DateField()
    tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tax_charge_type = models.CharField(max_length=10, choices=ChargeType.choices, blank=True, null=True)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    shipping_charge_type = models.CharField(max_length=10, choices=ChargeType.choices, blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_charge_type = models.CharField(max_length=10, choices=ChargeType.choices, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    objects = PurchaseOrderManager()

    def __str__(self):
        return self.description[:20]


class PurchaseOrderItem(CommonInfoAbstractModel):
    inventory_item = models.ForeignKey(
        "maintenance.Inventory",
        related_name="purchase_order_items",
        on_delete=models.CASCADE,
    )
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    purchase_order = models.ForeignKey(PurchaseOrder, related_name="items", on_delete=models.CASCADE)

    objects = PurchaseOrderItemManager()

    def __str__(self) -> str:
        return self.inventory_item.name


class PurchaseOrderAttachment(BaseAttachment, CommonInfoAbstractModel):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="attachments",
    )

    def __str__(self):
        return self.name


class Inventory(CommonInfoAbstractModel):
    name = models.CharField(max_length=255)
    item_type = models.ForeignKey(
        "system_preferences.InventoryItemType",
        related_name="inventory",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    description = models.TextField()
    part_number = models.CharField(max_length=100)
    vendor = models.ForeignKey(
        "people.Vendor",
        related_name="inventory",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    quantity = models.PositiveIntegerField()
    expense_account = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.ForeignKey(
        "system_preferences.InventoryLocation",
        related_name="inventory",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    bin_or_shelf_number = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class FixedAsset(CommonInfoAbstractModel):
    SLUG = "fda"

    class FixedAssetsStatus(models.TextChoices):
        IN_STORAGE = "in_storage", "In Storage"
        INSTALLED = "installed", "Installed"

    status = models.CharField(max_length=10, choices=FixedAssetsStatus.choices, blank=True, null=True)
    placed_in_service_date = models.DateField(blank=True, null=True)
    warranty_expiration_date = models.DateField(blank=True, null=True)
    unit = models.ForeignKey("property.Unit", on_delete=models.CASCADE, related_name="fixed_assets")
    inventory_item = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name="fixed_assets")
    quantity = models.IntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    objects = FixedAssetManager()

    def __str__(self):
        return self.inventory_item.name


@receiver(pre_save, sender=PurchaseOrderItem)
def set_purchase_order_item_cost(sender, instance, *args, **kwargs):
    instance.cost = instance.inventory_item.cost


@receiver(post_save, sender=FixedAsset)
def update_inventory_item_quantity(sender, instance, created, *args, **kwargs):
    if created:
        instance.inventory_item.quantity -= instance.quantity
        instance.inventory_item.save()
