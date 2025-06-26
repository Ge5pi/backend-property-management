import pytest
from django.utils import timezone

from lease.models import Lease

from ..models import Invoice
from ..tasks import create_invoices_of_units_task


@pytest.mark.django_db
def test_create_invoice_task(lease_factory):
    """
    Testing :py:func:`accounting.tasks.create_invoice`
    """
    lease_factory(status="ACTIVE", start_date=timezone.now().date() - timezone.timedelta(days=1))
    lease_1 = Lease.objects.get()

    create_invoices_of_units_task()

    assert Invoice.objects.count() == 1
    assert Invoice.objects.first().interval_start_date == lease_1.start_date

    create_invoices_of_units_task()

    assert Invoice.objects.count() == 1
