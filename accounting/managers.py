from django.db import models
from django.db.models import BooleanField, Case, DecimalField, ExpressionWrapper, F, PositiveIntegerField, Q, Sum, When
from django.db.models.functions import ExtractDay
from django.db.models.query import QuerySet
from django.utils import timezone

from core.managers import SlugQuerysetMixin
from property.models import PropertyLateFeePolicy


class InvoiceQuerySet(QuerySet, SlugQuerysetMixin):
    def annotate_data(self):
        return self.annotate(
            total_charges_amount=Sum("charges__amount", filter=Q(charges__charge_type="ONE_TIME"), default=0),
            charges_and_rent=F("total_charges_amount") + F("rent_amount"),
            recurring_charges_amount=Sum(
                "charges__amount",
                filter=Q(charges__parent_charge__isnull=False),
                default=0,
            )
            + F("rent_amount"),  # for internal use
            is_late_fee_applicable=ExpressionWrapper(
                Q(due_date__lt=timezone.now().date()), output_field=BooleanField()
            ),
            eligible_amount=Case(
                When(
                    parent_property__late_fee_policy__eligible_charges=PropertyLateFeePolicy.EligibleCharges.EVERY_CHARGE,  # noqa
                    then=F("charges_and_rent"),
                ),
                When(
                    parent_property__late_fee_policy__eligible_charges=PropertyLateFeePolicy.EligibleCharges.ONLY_RECURRING_RENT,  # noqa
                    then=F("rent_amount"),
                ),
                When(
                    parent_property__late_fee_policy__eligible_charges=PropertyLateFeePolicy.EligibleCharges.ALL_RECURRING_CHARGES,  # noqa
                    then=F("recurring_charges_amount"),
                ),
                default=F("rent_amount"),
            ),
            late_fee=Case(
                When(
                    parent_property__late_fee_policy__late_fee_type=PropertyLateFeePolicy.LateFeeType.FLAT,
                    then=F("parent_property__late_fee_policy__base_amount_fee"),
                ),
                When(
                    parent_property__late_fee_policy__late_fee_type=PropertyLateFeePolicy.LateFeeType.PERCENTAGE,
                    then=ExpressionWrapper(
                        F("parent_property__late_fee_policy__base_amount_fee") / 100 * F("eligible_amount"),
                        output_field=DecimalField(),
                    ),
                ),
                default=F("parent_property__late_fee_policy__base_amount_fee"),
            ),
            # Daily Late Fee
            number_of_days_late=ExpressionWrapper(
                ExtractDay(timezone.now() - F("due_date")),
                output_field=PositiveIntegerField(),
            ),
            daily_late_fee=F("number_of_days_late") * F("late_fee"),
            payable_late_fee=Case(
                When(
                    parent_property__late_fee_policy__charge_daily_late_fees=False,
                    then=F("late_fee"),
                ),
                When(
                    Q(parent_property__late_fee_policy__charge_daily_late_fees=True)
                    & Q(parent_property__late_fee_policy__daily_amount_per_month_max__gte=F("daily_late_fee")),
                    then=F("daily_late_fee"),
                ),
                When(
                    Q(parent_property__late_fee_policy__charge_daily_late_fees=True)
                    & Q(parent_property__late_fee_policy__daily_amount_per_month_max__lt=F("daily_late_fee")),
                    then=F("parent_property__late_fee_policy__daily_amount_per_month_max"),
                ),
                default=F("late_fee"),
            ),
            payable_amount=Case(
                When(
                    Q(is_late_fee_applicable=True),
                    then=F("charges_and_rent") + F("payable_late_fee") + F("arrears_amount"),
                ),
                When(
                    Q(is_late_fee_applicable=False),
                    then=F("charges_and_rent") + F("arrears_amount"),
                ),
                default=F("charges_and_rent") + F("arrears_amount"),
            ),
        )


InvoiceManager = models.Manager.from_queryset(InvoiceQuerySet)


class ChargeQuerySet(QuerySet, SlugQuerysetMixin):
    pass


ChargeManager = models.Manager.from_queryset(ChargeQuerySet)
