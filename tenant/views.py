import stripe
from django.db.models import Prefetch
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from djstripe.event_handlers import djstripe_receiver  # type: ignore[import-untyped]
from djstripe.models import PaymentIntent  # type: ignore[import-untyped]
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings

from accounting.filters import ChargeFilter, InvoiceFilter
from accounting.models import Charge, Invoice, Payment, PaymentStatusChoices
from accounting.serializers import ChargeSerializer, InvoiceSerializer, PaymentSerializer
from communication.models import Announcement, Contact
from communication.serializers import AnnouncementSerializer, ContactSerializer
from core.mixins import FilterQuerysetByAssociatedSubscriptionMixin
from lease.models import Lease
from lease.serializers import LeaseSerializer
from maintenance.filters import ServiceRequestFilter
from maintenance.models import ServiceRequest, WorkOrder
from maintenance.serializers import ServiceRequestSerializer, WorkOrderSerializer
from people.models import Tenant
from people.serializers import TenantSerializer

from .permissions import IsTenantAndActivePermission
from .serializers import PaymentIntentForInvoiceSerializer

tenant_permissions = [*api_settings.DEFAULT_PERMISSION_CLASSES, IsTenantAndActivePermission]


class WorkOrderViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ReadOnlyModelViewSet):
    queryset = (
        WorkOrder.objects.all()
        .annotate_slug()  # type: ignore[attr-defined]
        .order_by("-pk")
        .select_related("vendor_type", "vendor", "assign_to", "service_request")
    )
    serializer_class = WorkOrderSerializer
    permission_classes = tenant_permissions  # type: ignore[assignment]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.tenants.exists():
            tenant = self.request.user.tenants.latest("created_at")
            return qs.filter(
                service_request_id__in=tenant.lease.unit.service_requests.values_list("id", flat=True)
            ).order_by("-pk")
        else:
            return qs.none()


class ServiceRequestViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = (
        ServiceRequest.objects.annotate_slug().annotate_data().select_related("unit")  # type: ignore[attr-defined]
    )
    serializer_class = ServiceRequestSerializer
    permission_classes = tenant_permissions  # type: ignore[assignment]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = ServiceRequestFilter
    search_fields = ["subject", "description", "slug"]
    ordering_fields = ["subject", "description"]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.tenants.exists():
            tenant = self.request.user.tenants.latest("created_at")
            return qs.filter(unit=tenant.lease.unit).order_by("-pk")
        else:
            return qs.none()


class LeaseViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Lease.objects.prefetch_related("primary_tenant", "rental_application", "unit")
    serializer_class = LeaseSerializer
    permission_classes = tenant_permissions  # type: ignore[assignment]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.tenants.exists():
            tenant = self.request.user.tenants.latest("created_at")
            return qs.filter(primary_tenant=tenant, status="ACTIVE").order_by("-pk")
        else:
            return qs.none()


class AnnouncementViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Announcement.objects.all().prefetch_related("units", "properties")
    serializer_class = AnnouncementSerializer
    permission_classes = tenant_permissions  # type: ignore[assignment]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.tenants.exists():
            tenant = self.request.user.tenants.latest("created_at")
            return qs.filter(units=tenant.lease.unit).order_by("-pk")
        else:
            return qs.none()


class ChargeViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ReadOnlyModelViewSet):
    queryset = (
        Charge.objects.annotate_slug()  # type: ignore[attr-defined]
        .select_related("tenant", "parent_property", "unit", "parent_charge", "invoice")
        .order_by("-pk")
    )
    serializer_class = ChargeSerializer
    permission_classes = tenant_permissions  # type: ignore[assignment]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ["title", "amount", "status", "created_at"]
    filterset_class = ChargeFilter

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.tenants.exists():
            tenant = self.request.user.tenants.latest("created_at")
            return qs.filter(tenant=tenant).order_by("-pk")
        else:
            return qs.none()


class InvoiceViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ReadOnlyModelViewSet):
    queryset = (
        Invoice.objects.annotate_slug()  # type: ignore[attr-defined]
        .annotate_data()
        .select_related("business_information", "lease", "parent_property", "unit")
        .order_by("-pk")
    )
    serializer_class = InvoiceSerializer
    permission_classes = tenant_permissions  # type: ignore[assignment]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ["due_date", "rent_amount"]
    filterset_class = InvoiceFilter

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.tenants.exists():
            tenant = self.request.user.tenants.latest("created_at")
            return qs.filter(unit=tenant.lease.unit, lease=tenant.lease).order_by("-pk")
        else:
            return qs.none()

    @action(detail=True, methods=["get"], permission_classes=[IsTenantAndActivePermission], url_path="mark-as-paid")
    def mark_as_paid(self, request, pk=None):
        invoice = self.get_object()
        invoice.status = PaymentStatusChoices.PAID_NOT_VERIFIED
        invoice.payed_at = timezone.now().date()
        invoice.payed_late_fee = invoice.payable_late_fee
        invoice.total_paid_amount = invoice.payable_amount or 0
        invoice.save()
        invoice.charges.update(status=PaymentStatusChoices.PAID_NOT_VERIFIED)
        return Response(status=status.HTTP_200_OK)


class ContactViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Contact.objects.all().order_by("-pk")
    serializer_class = ContactSerializer
    permission_classes = tenant_permissions  # type: ignore[assignment]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "email", "primary_contact"]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(display_to_tenants=True).order_by("-pk")


class PaymentViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = (
        Payment.objects.all()
        .prefetch_related("account", Prefetch("invoice", Invoice.objects.annotate_slug()))  # type: ignore[attr-defined]
        .order_by("-pk")
    )
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = {"payment_date": ["gte", "lte"], "invoice__status": ["exact"]}
    search_fields = ["account__account_title", "amount"]
    ordering_fields = ["payment_date", "amount", "invoice__status"]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.tenants.exists():
            tenant = self.request.user.tenants.latest("created_at")
            return qs.filter(invoice__lease=tenant.lease).order_by("-pk")
        else:
            return qs.none()


class PaymentIntentForInvoiceCreateAPIView(FilterQuerysetByAssociatedSubscriptionMixin, generics.CreateAPIView):
    serializer_class = PaymentIntentForInvoiceSerializer
    permission_classes = [IsTenantAndActivePermission, permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice = serializer.validated_data["invoice"]
        invoice = Invoice.objects.annotate_data().get(pk=invoice.pk)
        customer_id = request.user.stripe_customer.id if request.user.stripe_customer else None
        intent = stripe.PaymentIntent.create(
            customer=customer_id,
            setup_future_usage="off_session",
            amount=int(invoice.payable_amount * 100),
            currency="usd",
            automatic_payment_methods={
                "enabled": True,
            },
            metadata={"invoice_id": invoice.id},
        )
        PaymentIntent.sync_from_stripe_data(intent)
        return Response({"client_secret": intent.client_secret}, status=status.HTTP_201_CREATED)


class TenantRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Tenant.objects.annotate_status().select_related("lease", "user").order_by("-pk")
    serializer_class = TenantSerializer
    permission_classes = [IsTenantAndActivePermission, permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.tenants.exists():
            tenant = self.request.user.tenants.latest("created_at")
            return qs.get(pk=tenant.pk)
        else:
            return qs.none()

    def get_object(self):
        return self.get_queryset() or None


@djstripe_receiver("payment_intent.succeeded")
def invoice_payment_succeeded(event, **kwargs):
    metadata = event.data["object"]["metadata"]
    invoice = Invoice.objects.annotate_data().get(pk=metadata["invoice_id"])
    invoice.status = PaymentStatusChoices.PAID_VERIFIED
    invoice.payed_at = timezone.now().date()
    if invoice.payable_late_fee > 0:
        invoice.payed_late_fee = invoice.payable_late_fee
    else:
        invoice.payed_late_fee = 0
    invoice.payed_late_fee = invoice.payable_late_fee
    invoice.total_paid_amount = invoice.payable_amount
    invoice.save()
    invoice.charges.update(status=PaymentStatusChoices.PAID_VERIFIED)

    return Response(status=200)
