import pytest

from accounting.models import GeneralLedgerAccount


@pytest.mark.django_db
def test_set_unit_type_info_in_unit(unit_type_factory, unit_factory):
    """
    Testing :py:func:`property.models.set_unit_type_info_in_unit` signal
    """
    unit_type = unit_type_factory()
    unit = unit_factory(unit_type=unit_type)

    assert unit.market_rent == unit_type.market_rent
    assert unit.future_market_rent == unit_type.future_market_rent
    assert unit.effective_date == unit_type.effective_date
    assert unit.application_fee == unit_type.application_fee
    assert unit.estimate_turn_over_cost == unit_type.estimate_turn_over_cost


@pytest.mark.django_db
def test_create_unit_general_ledger_accounts(unit_factory):
    """
    Testing :py:func:`property.signals.create_unit_general_ledger_accounts` signal
    """
    unit = unit_factory()
    accounts = GeneralLedgerAccount.objects.filter(
        account_holder_content_type__model="unit", account_holder_object_id=unit.id
    )

    assert accounts.count() == 14
    assert accounts.filter(account_type="ASSET", sub_account_type="RECEIVABLES", label=None).count() == 1
    assert accounts.filter(account_type="ASSET", sub_account_type="RECEIVABLES", label="SALES_TAX").count() == 1
    assert accounts.filter(account_type="ASSET", sub_account_type="INVENTORY", label=None).count() == 1
    assert accounts.filter(account_type="ASSET", sub_account_type="FIXED_ASSETS", label=None).count() == 1
    assert accounts.filter(account_type="INCOME", sub_account_type="DIRECT_INCOME", label=None).count() == 1
    assert accounts.filter(account_type="INCOME", sub_account_type="INDIRECT_INCOME", label=None).count() == 1
    assert accounts.filter(account_type="EXPENSE", sub_account_type="DIRECT_EXPENSE", label=None).count() == 1
    assert accounts.filter(account_type="EXPENSE", sub_account_type="INDIRECT_EXPENSE", label=None).count() == 1
    assert accounts.filter(account_type="LIABILITY", sub_account_type="CURRENT_LIABILITY", label=None).count() == 1
    assert accounts.filter(account_type="LIABILITY", sub_account_type="NON_CURRENT_LIABILITY", label=None).count() == 1
    assert accounts.filter(account_type="ASSET", sub_account_type="RECEIVABLES", label="LATE_FEE").count() == 1
    assert accounts.filter(account_type="INCOME", sub_account_type="INDIRECT_INCOME", label="LATE_FEE").count() == 1
    assert accounts.filter(account_type="ASSET", sub_account_type="RECEIVABLES", label="CHARGE").count() == 1
    assert accounts.filter(account_type="INCOME", sub_account_type="INDIRECT_INCOME", label="CHARGE").count() == 1
