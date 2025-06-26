from datetime import timedelta

import pytest

from accounting.utils import create_invoice_for_unit_lease

from ..models import Lease, RentalApplication


@pytest.mark.django_db
def test_rental_application_manager_slug_queryset(rental_application_factory):
    """
    Testing :py:meth:`lease.models.RentalApplicationQuerySet.annotate_slug`.
    """
    rental_application = rental_application_factory()
    rental_applications = RentalApplication.objects.annotate_slug()  # type: ignore[attr-defined]
    assert rental_applications.count() == 1
    assert rental_applications.get().slug == f"{RentalApplication.SLUG}-{rental_application.id}"


@pytest.mark.django_db
def test_lease_manager_next_invoice_date_queryset(lease_factory, invoice_factory):
    """
    Testing :py:meth:`lease.models.LeaseQuerySet.annotate_next_invoice_date`.
    """
    lease_1 = lease_factory(rent_cycle="WEEKLY", status="ACTIVE")
    create_invoice_for_unit_lease(lease_1.unit)

    lease_2 = lease_factory(rent_cycle="MONTHLY", status="ACTIVE")

    leases = Lease.objects.annotate_next_invoice_date()
    lease_1 = leases.get(id=lease_1.id)
    lease_2 = leases.get(id=lease_2.id)

    assert lease_1.next_invoice_date is not None
    assert lease_1.next_invoice_date.date() == lease_1.invoices.last().interval_end_date + timedelta(days=1)
    assert lease_2.next_invoice_date.date() == lease_2.start_date + timedelta(days=1)
