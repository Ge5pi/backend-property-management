from datetime import timedelta
from typing import Optional

from django.db.models import Q, Sum
from django.utils import timezone

from lease.models import Lease
from property.models import PropertyLateFeePolicy, Unit
from system_preferences.models import BusinessInformation

from .models import Charge, ChargeTypeChoices, Invoice, PaymentStatusChoices


def create_invoice_for_unit_lease(unit: Unit) -> Optional[Invoice]:
    """
    NOTE Only creates invoice when its next day of last invoice end interval or start of lease date if no invoice exists
    """

    late_fee_policy = (
        PropertyLateFeePolicy.objects.filter(parent_property=unit.parent_property).annotate_is_expired().first()
    )
    recurring_charges = Charge.objects.filter(charge_type=ChargeTypeChoices.RECURRING)

    for charge in recurring_charges:
        required_keys = [
            "title",
            "description",
            "amount",
            "gl_account",
            "tenant_id",
            "parent_property_id",
            "unit_id",
            "notes",
        ]
        charge_dict = charge.__dict__
        charge_data = {key: charge_dict[key] for key in required_keys}  # type: ignore[index]
        Charge.objects.create(
            charge_type=ChargeTypeChoices.ONE_TIME,
            status=PaymentStatusChoices.UNPAID,
            parent_charge=charge,
            subscription=unit.subscription,
            **charge_data,
        )

    if not late_fee_policy.is_expired:
        if late_fee_policy.grace_period_type == PropertyLateFeePolicy.GracePeriodType.NUMBER_OF_DAY:
            due_date = timezone.now() + timedelta(days=late_fee_policy.grace_period)
        elif late_fee_policy.grace_period_type == PropertyLateFeePolicy.GracePeriodType.TILL_DATE_OF_MONTH:
            due_date = timezone.now().replace(day=late_fee_policy.grace_period)
        else:
            due_date = timezone.now()
    else:
        due_date = timezone.now()

    lease = Lease.objects.filter(unit=unit, status=Lease.LeaseStatus.ACTIVE).first()
    if not lease:
        return None

    charges = Charge.objects.filter(
        unit=unit,
        status=PaymentStatusChoices.UNPAID,
        charge_type=ChargeTypeChoices.ONE_TIME,
        invoice=None,
        created_at__month=timezone.now().month,
    )
    business_info = BusinessInformation.objects.first()

    if lease.invoices.exists():  # type: ignore[union-attr]
        last_invoice: Invoice = lease.invoices.all().order_by("-created_at").first()  # type: ignore[union-attr]
        invoice_start_date = last_invoice.interval_end_date + timedelta(days=1)
    else:
        invoice_start_date = lease.start_date  # type: ignore[union-attr]

    if lease.rent_cycle == Lease.RentCycleChoices.WEEKLY:  # type: ignore[union-attr]
        invoice_end_date = invoice_start_date + timedelta(weeks=1)
    elif lease.rent_cycle == Lease.RentCycleChoices.YEARLY:  # type: ignore[union-attr]
        invoice_end_date = invoice_start_date + timedelta(days=365)
    elif lease.rent_cycle == Lease.RentCycleChoices.QUARTERLY:  # type: ignore[union-attr]
        invoice_end_date = invoice_start_date + timedelta(days=91)
    elif lease.rent_cycle == Lease.RentCycleChoices.SIX_MONTHS:  # type: ignore[union-attr]
        invoice_end_date = invoice_start_date + timedelta(days=182)
    else:
        invoice_end_date = invoice_start_date + timedelta(days=30)

    invoice = Invoice.objects.create(  # type: ignore[misc]
        business_information=business_info,
        lease=lease,
        parent_property=unit.parent_property,
        unit=unit,
        interval_start_date=invoice_start_date,
        interval_end_date=invoice_end_date,
        due_date=due_date.date(),
        rent_amount=lease.amount,  # type: ignore[union-attr]
        subscription=unit.subscription,
    )
    charges.update(invoice=invoice)
    pending_previous_invoices = (
        Invoice.objects.filter(unit=unit, lease=lease)
        .filter(Q(status=PaymentStatusChoices.UNPAID) | Q(status=PaymentStatusChoices.REJECTED))
        .exclude(pk=invoice.pk)
    )
    pending_previous_invoices.update(arrear_of=invoice, arrears_amount=0)
    invoice.arrears_amount = (
        pending_previous_invoices.annotate_data().aggregate(payable_arrears_amount=Sum("payable_amount"))[
            "payable_arrears_amount"
        ]
        or 0
    )
    invoice.save()
    return invoice
