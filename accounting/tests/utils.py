from datetime import timedelta

import pytest
from django.utils import timezone

from lease.models import Lease
from property.models import PropertyLateFeePolicy

from ..models import Invoice
from ..utils import create_invoice_for_unit_lease


@pytest.mark.django_db
def test_create_invoice_for_unit_lease(unit_factory, lease_factory, charge_factory):
    """
    Testing :py:func:`accounting.utils.create_invoice_for_unit_lease`
    """

    create_invoice_for_unit_lease(unit_factory())

    assert Invoice.objects.count() == 0

    lease_1 = lease_factory(status="ACTIVE")
    lease_1 = Lease.objects.get(id=lease_1.id)

    charge_factory(
        status=None,
        tenant_id=lease_1.primary_tenant.id,
        unit=lease_1.unit,
        parent_property=lease_1.unit.parent_property,
        charge_type="RECURRING",
        invoice=None,
    )

    create_invoice_for_unit_lease(lease_1.unit)

    assert Invoice.objects.count() == 1
    assert Invoice.objects.first().interval_start_date == lease_1.start_date

    create_invoice_for_unit_lease(lease_1.unit)

    assert Invoice.objects.count() == 2
    assert Invoice.objects.last().interval_start_date == Invoice.objects.first().interval_end_date + timedelta(days=1)

    lease_2 = lease_factory(status="ACTIVE", rent_cycle="WEEKLY")
    lease_2.unit.parent_property.late_fee_policy.grace_period_type = (
        PropertyLateFeePolicy.GracePeriodType.NUMBER_OF_DAY
    )
    lease_2.unit.parent_property.late_fee_policy.grace_period = 5
    lease_2.unit.parent_property.late_fee_policy.save()
    create_invoice_for_unit_lease(lease_2.unit)

    lease_3 = lease_factory(status="ACTIVE", rent_cycle="QUARTERLY")
    lease_3.unit.parent_property.late_fee_policy.grace_period_type = (
        PropertyLateFeePolicy.GracePeriodType.TILL_DATE_OF_MONTH
    )
    lease_3.unit.parent_property.late_fee_policy.grace_period = 5
    lease_3.unit.parent_property.late_fee_policy.save()
    create_invoice_for_unit_lease(lease_3.unit)

    lease_4 = lease_factory(status="ACTIVE", rent_cycle="YEARLY")
    lease_4.unit.parent_property.late_fee_policy.end_date = timezone.now() - timedelta(days=1)
    lease_4.unit.parent_property.late_fee_policy.save()
    create_invoice_for_unit_lease(lease_4.unit)

    lease_5 = lease_factory(status="ACTIVE", rent_cycle="SIX_MONTHS")
    create_invoice_for_unit_lease(lease_5.unit)

    assert Invoice.objects.latest("pk").arrears_amount == 0
    create_invoice_for_unit_lease(lease_5.unit)
    create_invoice_for_unit_lease(lease_5.unit)
    assert Invoice.objects.latest("pk").arrears_amount > 0
