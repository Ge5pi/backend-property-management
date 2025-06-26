from django.core.management.base import BaseCommand
from django.utils import timezone

from accounting.utils import create_invoice_for_unit_lease
from lease.models import Lease
from property.models import Unit


class Command(BaseCommand):
    help = "Create invoices for all units"

    def handle(self, *args, **kwargs):
        leases = Lease.objects.annotate_next_invoice_date().filter(
            status=Lease.LeaseStatus.ACTIVE,
            next_invoice_date__date=timezone.now().date(),
        )
        units = Unit.objects.filter(id__in=leases.values_list("unit_id", flat=True))
        for unit in units:
            create_invoice_for_unit_lease(unit)

        count = units.count()

        self.stdout.write(self.style.SUCCESS(f"Successfully created invoices for {count} units"))
