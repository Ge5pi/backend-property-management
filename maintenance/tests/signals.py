import pytest

from accounting.models import GeneralLedgerAccount


@pytest.mark.django_db
def test_update_inventory_item_quantity_signal(fixed_asset_factory, inventory_factory):
    """
    Testing :py:func:`maintenance.models.update_inventory_item_quantity` read
    """
    inventory = inventory_factory()
    initial_quantity = inventory.quantity
    fixed_asset = fixed_asset_factory(inventory_item=inventory)

    assert fixed_asset.inventory_item == inventory
    assert inventory.quantity == initial_quantity - fixed_asset.quantity


@pytest.mark.django_db
def test_set_purchase_order_item_cost(purchase_order_item_factory, inventory_factory):
    """
    Testing :py:func:`maintenance.models.set_purchase_order_item_cost` read
    """
    inventory = inventory_factory()
    purchase_order_item = purchase_order_item_factory(inventory_item=inventory)
    assert purchase_order_item.inventory_item == inventory
    assert purchase_order_item.cost == inventory.cost


@pytest.mark.django_db
def test_create_project_general_ledger_accounts(project_factory):
    """
    Testing :py:func:`maintenance.signals.create_project_general_ledger_accounts` signal
    """
    project = project_factory()
    accounts = GeneralLedgerAccount.objects.filter(
        account_holder_content_type__model="project", account_holder_object_id=project.id
    )

    assert accounts.count() == 1
    assert accounts.filter(account_type="EXPENSE", sub_account_type="INDIRECT_EXPENSE", label=None).count() == 1


@pytest.mark.django_db
def test_create_inventory_general_ledger_accounts(inventory_factory):
    """
    Testing :py:func:`maintenance.signals.create_inventory_general_ledger_accounts` signal
    """
    inventory = inventory_factory()
    accounts = GeneralLedgerAccount.objects.filter(
        account_holder_content_type__model="inventory", account_holder_object_id=inventory.id
    )

    assert accounts.count() == 1
    assert accounts.filter(account_type="ASSET", sub_account_type="INVENTORY", label=None).count() == 1
