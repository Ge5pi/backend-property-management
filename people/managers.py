from django.db import models
from django.db.models import Case, Count, Value, When
from django.db.models.query import QuerySet

from core.managers import SlugQuerysetMixin


class VendorTypeQuerySet(QuerySet, SlugQuerysetMixin):
    def annotate_vendor_count(self):
        return self.annotate(vendor_count=Count("vendors"))


VendorTypeManager = models.Manager.from_queryset(VendorTypeQuerySet)


class VendorQuerySet(QuerySet, SlugQuerysetMixin):
    pass


VendorManager = models.Manager.from_queryset(VendorQuerySet)


class TenantQuerySet(QuerySet):
    def annotate_status(self):
        from lease.models import Lease

        return self.annotate(
            status=Case(
                When(lease__status=Lease.LeaseStatus.ACTIVE, then=Value("Current")),
                default=Value("Past"),
            )
        )


TenantManager = models.Manager.from_queryset(TenantQuerySet)
