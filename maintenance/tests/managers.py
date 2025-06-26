from decimal import Decimal

import pytest
from pytest import approx

from .models import PurchaseOrder, PurchaseOrderItem, ServiceRequest, WorkOrder


@pytest.mark.django_db
def test_annotate_total_cost(purchase_order_item_factory, inventory_factory, purchase_order_factory):
    """
    Testing :py:meth:`maintenance.managers.PurchaseOrderItemQuerySet.annotate_total_cost`.
    """
    inventory = inventory_factory(cost="23.40")
    purchase_order = purchase_order_factory(
        tax=10,
        tax_charge_type="FLAT",
        discount=10,
        discount_charge_type="PERCENT",
    )
    purchase_order_item_factory(
        inventory_item=inventory,
        purchase_order=purchase_order,
        cost="23.40",
        quantity=9,
    )
    purchase_order_items = PurchaseOrderItem.objects.annotate_total_cost()
    assert purchase_order_items.get().item_cost == approx(Decimal("210.6"))
    assert purchase_order_items.get().tax_value == approx(Decimal("10"))
    assert purchase_order_items.get().discount_value == approx(Decimal("21.06"))
    assert purchase_order_items.get().total_cost == approx(Decimal("220.6") - Decimal("21.06"))


@pytest.mark.django_db
def test_annotate_sub_total_and_total(purchase_order_item_factory, inventory_factory, purchase_order_factory):
    """
    Testing :py:meth:`maintenance.models.PurchaseOrderQuerySet.annotate_sub_total_and_total`.
    """
    inventory = inventory_factory(cost="23.40")
    purchase_order = purchase_order_factory(
        tax=10,
        tax_charge_type="FLAT",
        shipping=10,
        shipping_charge_type="FLAT",
        discount=10,
        discount_charge_type="PERCENT",
    )
    purchase_order_item_factory(
        inventory_item=inventory,
        purchase_order=purchase_order,
        cost="23.40",
        quantity=9,
    )
    purchase_orders = PurchaseOrder.objects.annotate_sub_total_and_total()
    purchase_order = purchase_orders.get()
    assert purchase_order.sub_total == approx(Decimal("210.6"))
    assert purchase_order.tax_value == approx(Decimal("10"))
    assert purchase_order.shipping_value == approx(Decimal("10"))
    assert purchase_order.discount_value == approx(Decimal("21.06"))
    assert purchase_order.total == approx(Decimal("230.6") - Decimal("21.06"))


@pytest.mark.django_db
def test_purchase_order_manager_slug_queryset(purchase_order_factory):
    """
    Testing :py:meth:`maintenance.models.PurchaseOrderQuerySet.annotate_slug`.
    """
    purchase_order = purchase_order_factory()
    purchase_orders = PurchaseOrder.objects.annotate_slug()  # type: ignore[attr-defined]
    assert purchase_orders.count() == 1
    assert purchase_orders.get().slug == f"{PurchaseOrder.SLUG}-{purchase_order.id}"


@pytest.mark.django_db
def test_work_order_manager_slug_queryset(work_order_factory):
    """
    Testing :py:meth:`maintenance.models.WorkOrderQuerySet.annotate_slug`.
    """
    work_order = work_order_factory()
    work_orders = WorkOrder.objects.annotate_slug()  # type: ignore[attr-defined]
    assert work_orders.count() == 1
    assert work_orders.get().slug == f"{WorkOrder.SLUG}-{work_order.id}"


@pytest.mark.django_db
def test_service_request_manager_slug_queryset(service_request_factory):
    """
    Testing :py:meth:`maintenance.models.ServiceRequestQuerySet.annotate_slug`.
    """
    service_request = service_request_factory()
    service_requests = ServiceRequest.objects.annotate_slug()  # type: ignore[attr-defined]
    assert service_requests.count() == 1
    assert service_requests.get().slug == f"{ServiceRequest.SLUG}-{service_request.id}"


@pytest.mark.django_db
def test_service_request_manager_annotate_data_queryset(service_request_factory, lease_factory, work_order_factory):
    """
    Testing :py:meth:`maintenance.models.ServiceRequestQuerySet.annotate_data`.
    """

    lease = lease_factory(status="ACTIVE")
    service_request_1 = service_request_factory(unit=lease.unit)
    service_request_2 = service_request_factory()
    work_order_factory(service_request=service_request_2, status="COMPLETED")

    service_requests = ServiceRequest.objects.annotate_data()  # type: ignore[attr-defined]

    assert service_requests.count() == 2
    assert service_requests.get(id=service_request_1.id).work_order_count == 0
    assert service_requests.get(id=service_request_2.id).work_order_count == 1
    assert service_requests.get(id=service_request_1.id).tenant_id == lease.primary_tenant.id
    assert service_requests.get(id=service_request_2.id).tenant_id is None
    assert service_requests.get(id=service_request_1.id).status == "PENDING"
    assert service_requests.get(id=service_request_2.id).status == "COMPLETED"
