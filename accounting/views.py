from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, mixins, viewsets

from core.mixins import FilterQuerysetByAssociatedSubscriptionMixin

from .filters import ChargeFilter, InvoiceFilter
from .models import (
    Account,
    AccountAttachment,
    Charge,
    ChargeAttachment,
    GeneralLedgerAccount,
    GeneralLedgerTransaction,
    Invoice,
    Payment,
    PaymentAttachment,
)
from .serializers import (
    AccountAttachmentSerializer,
    AccountSerializer,
    ChargeAttachmentSerializer,
    ChargeSerializer,
    GeneralLedgerAccountSerializer,
    GeneralLedgerTransactionSerializer,
    InvoiceSerializer,
    PaymentAttachmentSerializer,
    PaymentSerializer,
)


class InvoiceViewSet(
    FilterQuerysetByAssociatedSubscriptionMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        Invoice.objects.annotate_slug()  # type: ignore[attr-defined]
        .annotate_data()
        .select_related("business_information", "lease", "parent_property", "unit")
        .order_by("-pk")
    )
    serializer_class = InvoiceSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["parent_property__name", "unit__name"]
    ordering_fields = ["due_date", "rent_amount"]
    filterset_class = InvoiceFilter


class ChargeViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = (
        Charge.objects.annotate_slug()  # type: ignore[attr-defined]
        .select_related("tenant", "parent_property", "unit", "parent_charge", "invoice")
        .order_by("-pk")
    )
    serializer_class = ChargeSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["title", "description", "tenant__first_name", "tenant__last_name"]
    ordering_fields = [
        "title",
        "amount",
        "status",
        "created_at",
    ]
    filterset_class = ChargeFilter


class ChargeAttachmentViewSet(
    FilterQuerysetByAssociatedSubscriptionMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ChargeAttachment.objects.all()
    serializer_class = ChargeAttachmentSerializer


class ChargeAttachmentByChargeListAPIView(FilterQuerysetByAssociatedSubscriptionMixin, generics.ListAPIView):
    queryset = ChargeAttachment.objects.all()
    serializer_class = ChargeAttachmentSerializer

    def get_queryset(self):
        return super().get_queryset().filter(charge=self.kwargs.get("charge_id")).order_by("-pk")


class AccountViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = Account.objects.all().order_by("-pk")
    serializer_class = AccountSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["account_title", "bank_name", "account_number"]
    ordering_fields = ["account_title", "bank_name", "account_number"]


class AccountAttachmentViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = AccountAttachment.objects.all().order_by("-pk")
    serializer_class = AccountAttachmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["account"]


class PaymentViewSet(
    FilterQuerysetByAssociatedSubscriptionMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        Payment.objects.all()
        .prefetch_related("account", Prefetch("invoice", Invoice.objects.annotate_slug()))  # type: ignore[attr-defined]
        .order_by("-pk")
    )
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = {
        "payment_date": ["gte", "lte"],
        "invoice__status": ["exact"],
        "invoice__lease__rental_application__applicant": ["exact"],
    }
    search_fields = ["account__account_title", "amount"]
    ordering_fields = ["payment_date", "amount", "invoice__status"]


class PaymentAttachmentViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = PaymentAttachment.objects.all().order_by("-pk")
    serializer_class = PaymentAttachmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["payment"]


class GeneralLedgerAccountViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ReadOnlyModelViewSet):
    queryset = GeneralLedgerAccount.objects.all().select_related("account_holder_content_type").order_by("-pk")
    serializer_class = GeneralLedgerAccountSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ["account_holder_content_type__model"]
    ordering_fields = ["account_holder_content_type__model", "account_type", "sub_account_type"]
    filterset_fields = ["account_type", "sub_account_type"]


class GeneralLedgerTransactionViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ReadOnlyModelViewSet):
    queryset = GeneralLedgerTransaction.objects.select_related("gl_account").order_by("-pk")
    serializer_class = GeneralLedgerTransactionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ["gl_account__account_holder_content_type__model"]
    ordering_fields = ["transaction_type", "amount"]
    filterset_fields = ["transaction_type", "gl_account", "gl_account__account_type"]
