from decimal import Decimal

from django.db import models
from django.db.models import Case, Count, ExpressionWrapper, F, OuterRef, Subquery, Sum, Value, When
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet

from core.managers import SlugQuerysetMixin
from lease.models import Lease


class ServiceRequestQuerySet(QuerySet, SlugQuerysetMixin):
    def annotate_data(self):
        from .models import WorkOrder

        return self.annotate(
            tenant_id=Case(
                When(
                    unit__leases__status="ACTIVE",
                    then=Subquery(
                        Lease.objects.filter(unit_id=OuterRef("unit_id"), status="ACTIVE").values("primary_tenant")[
                            :1
                        ],
                        output_field=models.IntegerField(),
                    ),
                ),
                default=Value(None),
            ),
            work_order_count=Count("work_orders"),
            status=Case(
                When(
                    work_order_count__gt=0,
                    then=Case(
                        When(
                            work_orders__status=WorkOrder.StatusChoices.COMPLETED,
                            then=Value("COMPLETED"),
                        ),
                        default=Value("PENDING"),
                    ),
                ),
                default=Value("PENDING"),
            ),
        )


ServiceRequestManager = models.Manager.from_queryset(ServiceRequestQuerySet)


class WorkOrderQuerySet(QuerySet, SlugQuerysetMixin):
    pass


WorkOrderManager = models.Manager.from_queryset(WorkOrderQuerySet)


class FixedAssetQuerySet(QuerySet, SlugQuerysetMixin):
    pass


FixedAssetManager = models.Manager.from_queryset(FixedAssetQuerySet)


class PurchaseOrderItemQuerySet(QuerySet):
    def annotate_total_cost(self):
        from .models import ChargeType

        return self.annotate(
            item_cost=models.ExpressionWrapper(F("quantity") * F("cost"), output_field=models.DecimalField()),
            tax_value=Case(
                When(
                    purchase_order__tax_charge_type=ChargeType.FLAT,
                    then=ExpressionWrapper(F("purchase_order__tax"), output_field=models.DecimalField()),
                ),
                When(
                    purchase_order__tax_charge_type=ChargeType.PERCENT,
                    then=ExpressionWrapper(
                        F("item_cost") * F("purchase_order__tax") / 100,
                        output_field=models.DecimalField(),
                    ),
                ),
                default=Decimal(0),
            ),
            discount_value=Case(
                When(
                    purchase_order__discount_charge_type=ChargeType.FLAT,
                    then=ExpressionWrapper(F("purchase_order__discount"), output_field=models.DecimalField()),
                ),
                When(
                    purchase_order__discount_charge_type=ChargeType.PERCENT,
                    then=ExpressionWrapper(
                        F("item_cost") * F("purchase_order__discount") / 100,
                        output_field=models.DecimalField(),
                    ),
                ),
                default=Decimal(0),
            ),
            total_cost=models.ExpressionWrapper(
                F("item_cost") + F("tax_value") - F("discount_value"),
                output_field=models.DecimalField(),
            ),
        )


PurchaseOrderItemManager = models.Manager.from_queryset(PurchaseOrderItemQuerySet)


class PurchaseOrderQuerySet(QuerySet, SlugQuerysetMixin):
    def annotate_sub_total_and_total(self):
        from .models import ChargeType, PurchaseOrderItem

        purchase_order_item_subquery = (
            PurchaseOrderItem.objects.filter(purchase_order=OuterRef("pk"))
            .annotate_total_cost()
            .values("purchase_order")
            .annotate(
                total_cost_sum=Sum("total_cost"),
                discount_sum=Sum("discount_value"),
                tax_sum=Sum("tax_value"),
                item_cost_sum=Sum("item_cost"),
            )
        )
        item_cost_subquery = purchase_order_item_subquery.values("item_cost_sum")
        total_cost_subquery = purchase_order_item_subquery.values("total_cost_sum")
        discount_subquery = purchase_order_item_subquery.values("discount_sum")
        tax_subquery = purchase_order_item_subquery.values("tax_sum")
        return self.annotate(
            sub_total=Coalesce(
                Subquery(item_cost_subquery, output_field=models.DecimalField()),
                Decimal(0),
            ),
            total_cost_sum=Coalesce(
                Subquery(total_cost_subquery, output_field=models.DecimalField()),
                Decimal(0),
            ),
            tax_value=Coalesce(
                Subquery(tax_subquery, output_field=models.DecimalField()),
                Decimal(0),
            ),
            discount_value=Coalesce(
                Subquery(discount_subquery, output_field=models.DecimalField()),
                Decimal(0),
            ),
            shipping_value=Case(
                When(
                    shipping_charge_type=ChargeType.FLAT,
                    then=ExpressionWrapper(F("shipping"), output_field=models.DecimalField()),
                ),
                When(
                    shipping_charge_type=ChargeType.PERCENT,
                    then=ExpressionWrapper(
                        F("sub_total") * F("shipping") / 100,
                        output_field=models.DecimalField(),
                    ),
                ),
                default=Decimal(0),
            ),
            total=ExpressionWrapper(
                F("total_cost_sum") + F("shipping_value"),
                output_field=models.DecimalField(),
            ),
        )


PurchaseOrderManager = models.Manager.from_queryset(PurchaseOrderQuerySet)
