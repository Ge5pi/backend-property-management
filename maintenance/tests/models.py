import pytest

from core.models import BaseAttachment, CommonInfoAbstractModel

from ..models import (
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


@pytest.mark.django_db
def test_work_order(
    work_order_factory,
    vendor_type_factory,
    vendor_factory,
    user_factory,
    service_request_factory,
):
    """
    Testing :py:class:`maintenance.models.Inventory` model with factory
    """
    vendor_type = vendor_type_factory()
    vendor = vendor_factory()
    user = user_factory()
    service_request = service_request_factory()
    work_order = work_order_factory(
        is_recurring=True,
        cycle="MONTHLY",
        status="OPEN",
        order_type="INTERNAL",
        job_description="Lorem ipsum dolor emit.",
        vendor_instructions="Lorem ipsum dolor emit.",
        vendor_trade="ABC",
        vendor_type=vendor_type,
        vendor=vendor,
        email_vendor=True,
        request_receipt=False,
        assign_to=user,
        owner_approved=False,
        follow_up_date="2020-12-12",
        service_request=service_request,
    )

    work_orders = WorkOrder.objects.annotate_slug()  # type: ignore[attr-defined]
    assert work_orders.count() == 1
    assert work_order.is_recurring
    assert work_order.cycle == "MONTHLY"
    assert work_order.status == "OPEN"
    assert work_order.order_type == "INTERNAL"
    assert work_order.job_description == "Lorem ipsum dolor emit."
    assert work_order.vendor_instructions == "Lorem ipsum dolor emit."
    assert work_order.vendor_trade == "ABC"
    assert work_order.vendor_type == vendor_type
    assert work_order.vendor == vendor
    assert work_order.email_vendor
    assert not work_order.request_receipt
    assert work_order.assign_to == user
    assert not work_order.owner_approved
    assert work_order.follow_up_date == "2020-12-12"
    assert work_order.service_request == service_request


@pytest.mark.django_db
def test_inventory(
    inventory_factory,
    vendor_factory,
    inventory_item_type_factory,
    inventory_location_factory,
):
    """
    Testing :py:class:`maintenance.models.Inventory` model with factory
    """

    vendor = vendor_factory()
    item_type = inventory_item_type_factory()
    location = inventory_location_factory()
    inventory = inventory_factory(
        item_type=item_type,
        vendor=vendor,
        location=location,
        description="Read line shake short term. Generation fine hotel word in religious energy.",
        part_number="2332",
        expense_account="677121438893",
        cost="23.40",
        bin_or_shelf_number="8880",
    )

    inventories = Inventory.objects.all()

    assert inventories.count() == 1
    assert inventory.pk is not None
    assert inventory.item_type == item_type
    assert inventory.location == location
    assert inventory.vendor == vendor
    assert inventory.description == "Read line shake short term. Generation fine hotel word in religious energy."
    assert inventory.part_number == "2332"
    assert inventory.expense_account == "677121438893"
    assert inventory.cost == "23.40"
    assert inventory.bin_or_shelf_number == "8880"
    assert str(inventory) == inventory.name
    assert issubclass(Inventory, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_fixed_asset(unit_factory, inventory_factory, fixed_asset_factory):
    """
    Testing :py:class:`maintenance.models.FixedAsset` model with factory
    """

    unit = unit_factory()
    inventory = inventory_factory()
    fixed_asset = fixed_asset_factory(
        unit=unit,
        inventory_item=inventory,
        status="in_storage",
        placed_in_service_date="2020-01-01",
        warranty_expiration_date="2020-01-01",
        quantity=9,
        cost="23.40",
    )

    fixed_assets = FixedAsset.objects.annotate_slug()  # type: ignore[attr-defined]

    assert fixed_assets.count() == 1
    assert fixed_asset.pk is not None
    assert fixed_asset.unit == unit
    assert fixed_asset.inventory_item == inventory
    assert fixed_asset.status == "in_storage"
    assert fixed_asset.placed_in_service_date == "2020-01-01"
    assert fixed_asset.warranty_expiration_date == "2020-01-01"
    assert fixed_asset.quantity == 9
    assert fixed_asset.cost == "23.40"
    assert str(fixed_asset) == fixed_asset.inventory_item.name
    assert issubclass(FixedAsset, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_purchase_order(purchase_order_factory, vendor_factory):
    """
    Testing :py:class:`maintenance.models.PurchaseOrder` model with factory
    """
    vendor = vendor_factory()
    purchase_order = purchase_order_factory(
        vendor=vendor,
        description="Read line shake short term. Generation fine hotel word in religious energy.",
        required_by_date="2020-01-01",
        tax=23,
        tax_charge_type="FLAT",
        shipping=23,
        shipping_charge_type="FLAT",
        discount=2,
        discount_charge_type="FLAT",
        notes="Read line shake short term. Generation fine hotel word in religious energy.",
    )
    purchase_orders = PurchaseOrder.objects.all()
    assert purchase_orders.count() == 1
    assert purchase_order.pk is not None
    assert purchase_order.vendor == vendor
    assert purchase_order.description == "Read line shake short term. Generation fine hotel word in religious energy."
    assert purchase_order.required_by_date == "2020-01-01"
    assert purchase_order.tax == 23
    assert purchase_order.tax_charge_type == "FLAT"
    assert purchase_order.shipping == 23
    assert purchase_order.shipping_charge_type == "FLAT"
    assert purchase_order.discount == 2
    assert purchase_order.discount_charge_type == "FLAT"
    assert purchase_order.notes == "Read line shake short term. Generation fine hotel word in religious energy."
    assert str(purchase_order) == purchase_order.description[:20]
    assert issubclass(PurchaseOrder, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_purchase_order_item(purchase_order_item_factory, inventory_factory, purchase_order_factory):
    """
    Testing :py:class:`maintenance.models.PurchaseOrderItem` model with factory
    """
    inventory = inventory_factory(cost="23.40")
    purchase_order = purchase_order_factory()
    purchase_order_item = purchase_order_item_factory(
        inventory_item=inventory,
        purchase_order=purchase_order,
        cost="23.40",
        quantity=9,
    )
    purchase_order_items = PurchaseOrder.objects.all()
    assert purchase_order_items.count() == 1
    assert purchase_order_item.pk is not None
    assert purchase_order_item.inventory_item == inventory
    assert purchase_order_item.purchase_order == purchase_order
    assert purchase_order_item.cost == "23.40"
    assert purchase_order_item.quantity == 9
    assert str(purchase_order_item) == str(inventory)
    assert issubclass(PurchaseOrderItem, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_purchase_order_attachment(purchase_order_attachment_factory, purchase_order_factory):
    """
    Testing :py:class:`maintenance.models.PurchaseOrderAttachment` model with factory
    """
    purchase_order = purchase_order_factory()
    purchase_order_attachment = purchase_order_attachment_factory(
        purchase_order=purchase_order,
        name="Fan",
        file="Fan.pdf",
        file_type="pdf",
    )
    purchase_order_attachments = PurchaseOrder.objects.all()
    assert purchase_order_attachments.count() == 1
    assert purchase_order_attachment.pk is not None
    assert purchase_order_attachment.purchase_order == purchase_order
    assert purchase_order_attachment.name == "Fan"
    assert purchase_order_attachment.file == "Fan.pdf"
    assert purchase_order_attachment.file_type == "pdf"
    assert str(purchase_order_attachment) == purchase_order_attachment.name
    assert issubclass(PurchaseOrderAttachment, BaseAttachment)


@pytest.mark.django_db
def test_service_request(service_request_factory, unit_factory):
    """
    Testing :py:class:`maintenance.models.ServiceRequest` model with factory
    """
    unit = unit_factory()
    service_request = service_request_factory(
        unit=unit,
        order_type="INTERNAL",
        permission_to_enter=True,
        subject="Problem with the AC",
        additional_information_for_entry="Read line shake short term. Generation fine hotel word in religious energy.",
        description="Read line shake short term. Generation fine hotel word in religious energy.",
        priority="LOW",
    )

    service_requests = ServiceRequest.objects.all()

    assert service_requests.count() == 1
    assert service_request.pk is not None
    assert service_request.unit == unit
    assert service_request.order_type == "INTERNAL"
    assert service_request.permission_to_enter
    assert (
        service_request.additional_information_for_entry
        == "Read line shake short term. Generation fine hotel word in religious energy."
    )
    assert service_request.description == "Read line shake short term. Generation fine hotel word in religious energy."
    assert service_request.priority == "LOW"
    assert service_request.subject == "Problem with the AC"
    assert str(service_request) == service_request.subject
    assert issubclass(ServiceRequest, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_service_request_attachment(service_request_attachment_factory, service_request_factory):
    """
    Testing :py:class:`communication.models.ServiceRequestAttachment` model with factory
    """
    service_request = service_request_factory()
    service_request_attachment = service_request_attachment_factory(
        name="Property Agreement", file="test.pdf", file_type="pdf", service_request=service_request
    )

    service_request_attachments = ServiceRequestAttachment.objects.all()
    assert service_request_attachments.count() == 1
    assert service_request_attachment.name == "Property Agreement"
    assert service_request_attachment.file == "test.pdf"
    assert service_request_attachment.file_type == "pdf"
    assert service_request_attachment.service_request == service_request
    assert str(service_request_attachment) == "Property Agreement"
    assert isinstance(service_request_attachment, BaseAttachment)


@pytest.mark.django_db
def test_labor(labor_factory, work_order_factory):
    """
    Testing :py:class:`maintenance.models.Labor` model with factory
    """
    work_order = work_order_factory()
    labor = labor_factory(
        work_order=work_order,
        title="Lorem ipsum dolor emit.",
        date="2020-01-01",
        hours=9,
        description="Read line shake short term. Generation fine hotel word in religious energy.",
    )

    labors = Labor.objects.all()

    assert labors.count() == 1
    assert labor.pk is not None
    assert labor.work_order == work_order
    assert labor.title == "Lorem ipsum dolor emit."
    assert labor.date == "2020-01-01"
    assert labor.hours == 9
    assert labor.description == "Read line shake short term. Generation fine hotel word in religious energy."
    assert str(labor) == labor.title
    assert issubclass(Labor, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_inspection(inspection_factory, unit_factory):
    """
    Testing :py:class:`maintenance.models.Inspection` model with factory
    """
    unit = unit_factory()
    inspection = inspection_factory(
        unit=unit,
        name="Lorem ipsum dolor emit.",
        date="2020-01-01",
    )

    inspections = Inspection.objects.all()

    assert inspections.count() == 1
    assert inspection.pk is not None
    assert inspection.unit == unit
    assert inspection.name == "Lorem ipsum dolor emit."
    assert inspection.date == "2020-01-01"
    assert str(inspection) == inspection.name
    assert issubclass(Inspection, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_area(area_factory, inspection_factory):
    """
    Testing :py:class:`maintenance.models.Area` model with factory
    """
    inspection = inspection_factory()
    area = area_factory(
        inspection=inspection,
        name="Lorem ipsum dolor emit.",
    )

    areas = Area.objects.all()

    assert areas.count() == 1
    assert area.pk is not None
    assert area.inspection == inspection
    assert area.name == "Lorem ipsum dolor emit."
    assert str(area) == area.name
    assert issubclass(Area, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_area_item(area_item_factory, area_factory):
    """
    Testing :py:class:`maintenance.models.AreaItem` model with factory
    """
    area = area_factory()
    area_item = area_item_factory(
        area=area,
        name="Lorem ipsum dolor emit.",
        condition="OKAY",
    )

    area_items = AreaItem.objects.all()

    assert area_items.count() == 1
    assert area_item.pk is not None
    assert area_item.area == area
    assert area_item.name == "Lorem ipsum dolor emit."
    assert area_item.condition == "OKAY"
    assert str(area_item) == area_item.name
    assert issubclass(AreaItem, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_project(project_factory, unit_factory):
    """
    Testing :py:class:`maintenance.models.Project` model with factory
    """
    unit = unit_factory()
    project = project_factory(
        parent_property=unit.parent_property,
        name="Lorem ipsum dolor emit.",
        description="Read line shake short term. Generation fine hotel word in religious energy.",
        status="PENDING",
        budget="23.40",
        gl_account="677121438893",
        start_date="2020-01-01",
        end_date="2020-01-01",
        select_all_units=False,
        units=[unit],
    )

    projects = Project.objects.all()

    assert projects.count() == 1
    assert project.pk is not None
    assert project.parent_property == unit.parent_property
    assert project.name == "Lorem ipsum dolor emit."
    assert project.description == "Read line shake short term. Generation fine hotel word in religious energy."
    assert project.status == "PENDING"
    assert project.budget == "23.40"
    assert project.gl_account == "677121438893"
    assert project.start_date == "2020-01-01"
    assert project.end_date == "2020-01-01"
    assert not project.select_all_units
    assert project.units.first() == unit
    assert str(project) == project.name
    assert issubclass(Project, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_project_expense_attachment(project_expense_attachment_factory, project_expense_factory):
    """
    Testing :py:class:`maintenance.models.PurchaseOrderAttachment` model with factory
    """
    project_expense = project_expense_factory()
    project_expense_attachment = project_expense_attachment_factory(
        project_expense=project_expense,
        name="Fan",
        file="Fan.pdf",
        file_type="pdf",
    )
    project_expense_attachments = ProjectExpenseAttachment.objects.all()
    assert project_expense_attachments.count() == 1
    assert project_expense_attachment.pk is not None
    assert project_expense_attachment.project_expense == project_expense
    assert project_expense_attachment.name == "Fan"
    assert project_expense_attachment.file == "Fan.pdf"
    assert project_expense_attachment.file_type == "pdf"
    assert str(project_expense_attachment) == project_expense_attachment.name
    assert issubclass(PurchaseOrderAttachment, BaseAttachment)


@pytest.mark.django_db
def test_project_expense(project_expense_factory, project_factory, user_factory):
    """
    Testing :py:class:`maintenance.models.ProjectExpense` model with factory
    """
    project = project_factory()
    user = user_factory()
    project_expense = project_expense_factory(
        project=project,
        title="Fan",
        description="Fan",
        amount="23.40",
        date="2020-01-01",
        assigned_to=user,
    )
    project_expenses = ProjectExpense.objects.all()
    assert project_expenses.count() == 1
    assert project_expense.pk is not None
    assert project_expense.project == project
    assert project_expense.title == "Fan"
    assert project_expense.description == "Fan"
    assert project_expense.amount == "23.40"
    assert project_expense.date == "2020-01-01"
    assert project_expense.assigned_to == user
    assert str(project_expense) == project_expense.title
    assert issubclass(PurchaseOrderItem, CommonInfoAbstractModel)
