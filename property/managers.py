from django.db import models
from django.db.models import (
    BooleanField,
    Case,
    Count,
    Exists,
    ExpressionWrapper,
    F,
    Max,
    OuterRef,
    Q,
    Subquery,
    Value,
    When,
)
from django.db.models.functions import ExtractDay
from django.db.models.query import QuerySet
from django.utils import timezone

from core.managers import SlugQuerysetMixin


class PropertyQuerySet(QuerySet, SlugQuerysetMixin):
    def annotate_data(self):
        """
        Annotation to check if property is occupied and if late fee policy is configured
        """
        from property.models import Unit

        units = Unit.objects.filter(parent_property=OuterRef("pk"))
        active_lease_subquery = (
            Unit.objects.filter(parent_property=OuterRef("pk")).annotate_data().filter(is_occupied=True)
        )
        return self.annotate(
            number_of_units=Count("units", distinct=True),
            is_occupied=Case(
                When(~Exists(Subquery(units)), then=Value(None)),
                When(Exists(Subquery(active_lease_subquery)), then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
            is_late_fee_policy_configured=Case(
                When(
                    Q(late_fee_policy__late_fee_type__isnull=False)
                    & Q(late_fee_policy__eligible_charges__isnull=False),
                    then=Value(True),
                ),
                default=Value(False),
                output_field=BooleanField(),
            ),
        )

    def annotate_portfolio_data(self):
        return self.annotate(
            units_count=Count("units"),
            occupied_units_count=Count("units", filter=Q(units__leases__status="ACTIVE")),
            vacant_units_count=Count("units", filter=~Q(units__leases__status="ACTIVE")),
        )


class PropertyManager(models.Manager.from_queryset(PropertyQuerySet)):  # type: ignore[misc]
    def get_cover_picture(self, prop):
        cover_photos = prop.photos.filter(is_cover=True)
        if cover_photos.exists():
            return cover_photos.get()
        else:
            return prop.photos.first()


class UnitTypeManager(models.Manager):
    def get_cover_picture(self, unit_type):
        cover_photos = unit_type.photos.filter(is_cover=True)
        if cover_photos.exists():
            return cover_photos.get()
        else:
            return unit_type.photos.first()

    def apply_on_all_units(self, unit_type):
        return unit_type.units.update(
            market_rent=unit_type.market_rent,
            future_market_rent=unit_type.future_market_rent,
            effective_date=unit_type.effective_date,
            application_fee=unit_type.application_fee,
            estimate_turn_over_cost=unit_type.estimate_turn_over_cost,
        )


class UnitQuerySet(QuerySet, SlugQuerysetMixin):
    def annotate_data(self):
        from lease.models import Lease

        active_lease_subquery = Lease.objects.filter(unit_id=OuterRef("pk"), status=Lease.LeaseStatus.ACTIVE)
        closed_lease_subquery = Lease.objects.filter(unit_id=OuterRef("pk"), status=Lease.LeaseStatus.CLOSED)
        return self.annotate(
            is_occupied=Case(
                When(Exists(Subquery(active_lease_subquery)), then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
            lease_id=Subquery(
                active_lease_subquery.values("id")[:1],
                output_field=models.IntegerField(),
            ),
            tenant_id=Subquery(
                active_lease_subquery.values("primary_tenant__id")[:1],
                output_field=models.IntegerField(),
            ),
            tenant_first_name=Subquery(
                active_lease_subquery.values("primary_tenant__first_name")[:1],
                output_field=models.CharField(),
            ),
            tenant_last_name=Subquery(
                active_lease_subquery.values("primary_tenant__last_name")[:1],
                output_field=models.CharField(),
            ),
            vacant_for_days=Case(
                When(
                    ~Q(leases__status="ACTIVE") & Exists(Subquery(closed_lease_subquery)),
                    then=ExtractDay(
                        timezone.now().date()
                        - Max(
                            F("leases__end_date"),
                            output_field=models.DateField(),
                        )
                    ),
                ),
                When(
                    ~Q(leases__status="ACTIVE") & ~Exists(Subquery(closed_lease_subquery)),
                    then=ExtractDay(timezone.now().date() - F("created_at")),
                ),
                default=Value(None),
            ),
        )


class UnitManager(models.Manager.from_queryset(UnitQuerySet)):  # type: ignore[misc]
    def get_cover_picture(self, unit):
        cover_photos = unit.photos.filter(is_cover=True)
        if cover_photos.exists():
            return cover_photos.get()
        else:
            return unit.photos.first()


class LateFeePolicyQuerySet(QuerySet):
    def annotate_is_expired(self):
        return self.annotate(
            is_expired=ExpressionWrapper(Q(end_date__lt=timezone.now().date()), output_field=BooleanField())
        )


LateFeePolicyManager = models.Manager.from_queryset(LateFeePolicyQuerySet)
