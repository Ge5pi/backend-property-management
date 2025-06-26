from datetime import timedelta

from django.db import models
from django.db.models import Case, Exists, F, Max, OuterRef, Q, Subquery, Value, When
from django.db.models.query import QuerySet

from core.managers import SlugQuerysetMixin


class RentalApplicationQuerySet(QuerySet, SlugQuerysetMixin):
    pass


RentalApplicationManager = models.Manager.from_queryset(RentalApplicationQuerySet)


class LeaseQuerySet(QuerySet):
    def annotate_next_invoice_date(self):
        from accounting.models import Invoice
        from lease.models import Lease

        invoice_subquery = Invoice.objects.filter(lease_id=OuterRef("pk"))

        return self.annotate(
            next_invoice_date=Case(
                When(
                    Q(Exists(Subquery(invoice_subquery)) & Q(status=Lease.LeaseStatus.ACTIVE)),
                    then=Max(
                        F("invoices__interval_end_date"),
                        output_field=models.DateField(),
                    )
                    + timedelta(days=1),
                ),
                When(
                    Q(~Exists(Subquery(invoice_subquery))) & Q(status=Lease.LeaseStatus.ACTIVE),
                    then=F("start_date") + timedelta(days=1),
                ),
                default=Value(None),
            )
        )


LeaseManager = models.Manager.from_queryset(LeaseQuerySet)
