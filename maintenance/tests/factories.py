import random
from decimal import Decimal

import factory  # type: ignore[import]

from core.tests import BaseAttachmentFactory, SubscriptionAbstractFactory


class ServiceRequestFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "maintenance.ServiceRequest"

    unit = factory.SubFactory("property.tests.factories.UnitFactory")
    order_type = "RESIDENT"
    permission_to_enter = factory.Faker("boolean")
    additional_information_for_entry = factory.Faker("text")
    priority = "NORMAL"
    subject = factory.Faker("word")
    description = factory.Faker("text")


class ServiceRequestAttachmentFactory(BaseAttachmentFactory):
    class Meta:
        model = "maintenance.ServiceRequestAttachment"
        abstract = False

    service_request = factory.SubFactory("maintenance.tests.factories.ServiceRequestFactory")


class WorkOrderFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "maintenance.WorkOrder"

    is_recurring = factory.Faker("boolean")
    cycle = "MONTHLY"
    status = "OPEN"
    order_type = "RESIDENT"
    job_description = factory.Faker("text")
    vendor_instructions = factory.Faker("text")
    vendor_trade = "PLUMBER"
    vendor_type = factory.SubFactory("people.tests.factories.VendorTypeFactory")
    vendor = factory.SubFactory("people.tests.factories.VendorFactory")
    email_vendor = factory.Faker("boolean")
    request_receipt = factory.Faker("boolean")
    assign_to = factory.SubFactory("authentication.tests.factories.UserFactory")
    owner_approved = factory.Faker("boolean")
    follow_up_date = factory.Faker("date")
    service_request = factory.SubFactory("maintenance.tests.factories.ServiceRequestFactory")


class LaborFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "maintenance.Labor"

    title = factory.Faker("word")
    date = factory.Faker("date")
    hours = factory.Faker("random_number", digits=2)
    description = factory.Faker("text")
    work_order = factory.SubFactory(WorkOrderFactory)


class InspectionFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "maintenance.Inspection"

    name = factory.Faker("word")
    date = factory.Faker("date")
    unit = factory.SubFactory("property.tests.factories.UnitFactory")


class AreaFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "maintenance.Area"

    name = factory.Faker("word")
    inspection = factory.SubFactory(InspectionFactory)


class AreaItemFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "maintenance.AreaItem"

    name = factory.Faker("word")
    area = factory.SubFactory(AreaFactory)
    condition = "OKAY"


class ProjectFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "maintenance.Project"

    name = factory.Faker("word")
    description = factory.Faker("text")
    status = "PENDING"
    parent_property = factory.SubFactory("property.tests.factories.PropertyFactory")
    budget = factory.LazyFunction(lambda: Decimal(random.randrange(10000)) / 100)
    gl_account = factory.Faker("random_number", digits=12)
    start_date = factory.Faker("date")
    end_date = factory.Faker("date")
    select_all_units = False

    @factory.post_generation
    def units(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        for unit in extracted:
            self.units.add(unit)


class PurchaseOrderFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "maintenance.PurchaseOrder"

    vendor = factory.SubFactory("people.tests.factories.VendorFactory")
    description = factory.Faker("text")
    required_by_date = factory.Faker("date")
    tax = factory.Faker("pydecimal", min_value=0, max_value=1000, right_digits=2)
    tax_charge_type = "FLAT"
    shipping = factory.Faker("pydecimal", min_value=0, max_value=1000, right_digits=2)
    shipping_charge_type = "FLAT"
    discount = factory.Faker("pydecimal", min_value=0, max_value=1000, right_digits=2)
    discount_charge_type = "FLAT"
    notes = factory.Faker("text")


class PurchaseOrderItemFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "maintenance.PurchaseOrderItem"

    inventory_item = factory.SubFactory("maintenance.tests.factories.InventoryFactory")
    purchase_order = factory.SubFactory(PurchaseOrderFactory)
    cost = factory.Faker("pydecimal", min_value=0, max_value=1000, right_digits=2)
    quantity = factory.Faker("random_number", digits=2)


class PurchaseOrderAttachmentFactory(BaseAttachmentFactory):
    class Meta:
        model = "maintenance.PurchaseOrderAttachment"
        abstract = False

    purchase_order = factory.SubFactory(PurchaseOrderFactory)


class InventoryFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "maintenance.Inventory"

    name = factory.Faker("word")
    item_type = factory.SubFactory("system_preferences.tests.factories.InventoryItemTypeFactory")
    location = factory.SubFactory("system_preferences.tests.factories.InventoryLocationFactory")
    vendor = factory.SubFactory("people.tests.factories.VendorFactory")
    description = factory.Faker("text")
    part_number = factory.LazyFunction(lambda: str(factory.Faker("random_number", digits=4)))
    quantity = factory.Faker("random_number", digits=6)
    expense_account = factory.LazyFunction(lambda: str(factory.Faker("random_number", digits=12)))
    cost = factory.LazyFunction(lambda: Decimal(random.randrange(10000)) / 100)
    bin_or_shelf_number = factory.LazyFunction(lambda: str(factory.Faker("random_number", digits=4)))


class FixedAssetFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "maintenance.FixedAsset"

    status = "in_storage"
    placed_in_service_date = factory.Faker("date")
    warranty_expiration_date = factory.Faker("date")
    unit = factory.SubFactory("property.tests.factories.UnitFactory")
    inventory_item = factory.SubFactory(InventoryFactory)
    quantity = factory.Faker("random_number", digits=1)
    cost = factory.LazyFunction(lambda: Decimal(random.randrange(10000)) / 100)


class ProjectExpenseFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "maintenance.ProjectExpense"

    title = factory.Faker("word")
    description = factory.Faker("text")
    amount = factory.Faker("pydecimal", min_value=0, max_value=1000, right_digits=2)
    date = factory.Faker("date")
    assigned_to = factory.SubFactory("authentication.tests.factories.UserFactory")
    project = factory.SubFactory(ProjectFactory)


class ProjectExpenseAttachmentFactory(BaseAttachmentFactory):
    class Meta:
        model = "maintenance.ProjectExpenseAttachment"
        abstract = False

    project_expense = factory.SubFactory(ProjectExpenseFactory)
