from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from pytest import approx

from property.models import PropertyLateFeePolicy

from .models import Invoice


@pytest.mark.django_db
def test_invoice_annotate_data(invoice_factory, charge_factory):
    """
    Testing :py:meth:`accounting.models.InvoiceQuerySet.annotate_data`.
    """

    invoice_1 = invoice_factory(
        interval_start_date=datetime(2023, 1, 1),
        interval_end_date=datetime(2023, 1, 1),
        due_date=timezone.now().date() + timedelta(days=1),
        rent_amount=Decimal("100.00"),
        payed_at=datetime(2023, 1, 1),
        payed_late_fee=Decimal("10.00"),
        arrears_amount=Decimal("15.00"),
    )
    invoice_2 = invoice_factory(
        rent_amount=Decimal("100.00"),
        due_date=timezone.now().date() - timedelta(days=3),
        arrears_amount=Decimal("10.00"),
    )

    recurring_charge = charge_factory(invoice=invoice_1, amount=Decimal("30.00"), charge_type="RECURRING", status=None)
    charge_factory(invoice=invoice_1, amount=Decimal("10.00"))
    charge_factory(invoice=invoice_1, amount=Decimal("20.00"))
    charge_factory(invoice=invoice_1, amount=Decimal("30.00"), parent_charge=recurring_charge)

    invoice_1.parent_property.late_fee_policy.eligible_charges = PropertyLateFeePolicy.EligibleCharges.EVERY_CHARGE
    invoice_1.parent_property.late_fee_policy.late_fee_type = PropertyLateFeePolicy.LateFeeType.FLAT
    invoice_1.parent_property.late_fee_policy.base_amount_fee = Decimal("10.00")
    invoice_1.parent_property.late_fee_policy.save()

    invoice_2.parent_property.late_fee_policy.late_fee_type = PropertyLateFeePolicy.LateFeeType.FLAT
    invoice_2.parent_property.late_fee_policy.base_amount_fee = Decimal("10.00")
    invoice_2.parent_property.late_fee_policy.charge_daily_late_fees = False
    invoice_2.parent_property.late_fee_policy.save()

    invoices = Invoice.objects.annotate_data()
    invoice_1 = invoices.get(pk=invoice_1.pk)
    invoice_2 = invoices.get(pk=invoice_2.pk)

    assert invoice_1.total_charges_amount == approx(Decimal("60.00"))
    assert invoice_1.charges_and_rent == approx(Decimal("160.00"))
    assert invoice_1.recurring_charges_amount == approx(Decimal("130.00"))

    assert not invoice_1.is_late_fee_applicable
    assert invoice_2.is_late_fee_applicable

    assert invoice_1.eligible_amount == invoice_1.charges_and_rent

    invoice_1.parent_property.late_fee_policy.eligible_charges = (
        PropertyLateFeePolicy.EligibleCharges.ONLY_RECURRING_RENT
    )
    invoice_1.parent_property.late_fee_policy.save()
    invoice_1 = Invoice.objects.annotate_data().get(pk=invoice_1.pk)

    assert invoice_1.eligible_amount == invoice_1.rent_amount

    invoice_1.parent_property.late_fee_policy.eligible_charges = (
        PropertyLateFeePolicy.EligibleCharges.ALL_RECURRING_CHARGES
    )
    invoice_1.parent_property.late_fee_policy.save()
    invoice_1 = Invoice.objects.annotate_data().get(pk=invoice_1.pk)

    assert invoice_1.eligible_amount == invoice_1.recurring_charges_amount

    assert invoice_2.late_fee == approx(Decimal("10.00"))

    invoice_2.parent_property.late_fee_policy.late_fee_type = PropertyLateFeePolicy.LateFeeType.PERCENTAGE
    invoice_2.parent_property.late_fee_policy.save()
    invoice_2 = Invoice.objects.annotate_data().get(pk=invoice_2.pk)

    assert invoice_2.late_fee == approx(Decimal("10.00"))

    assert invoice_2.number_of_days_late == 3
    assert invoice_2.daily_late_fee == approx(Decimal("30.00"))
    assert invoice_2.payable_late_fee == approx(Decimal("10.00"))

    invoice_2.parent_property.late_fee_policy.charge_daily_late_fees = True
    invoice_2.parent_property.late_fee_policy.daily_amount_per_month_max = Decimal("50.00")
    invoice_2.parent_property.late_fee_policy.save()
    invoice_2 = Invoice.objects.annotate_data().get(pk=invoice_2.pk)

    assert invoice_2.payable_late_fee == approx(Decimal("30.00"))

    invoice_2.parent_property.late_fee_policy.daily_amount_per_month_max = Decimal("15.00")
    invoice_2.parent_property.late_fee_policy.save()
    invoice_2 = Invoice.objects.annotate_data().get(pk=invoice_2.pk)

    assert invoice_2.payable_late_fee == approx(Decimal("15.00"))

    assert invoice_2.payable_amount == approx(Decimal("125.00"))
    assert invoice_1.payable_amount == approx(Decimal("175.00"))

    invoice_1.arrears_amount = Decimal("10.00")
    invoice_1.save()

    invoice_1 = Invoice.objects.annotate_data().get(pk=invoice_1.pk)
    assert invoice_1.payable_amount == approx(Decimal("170.00"))
