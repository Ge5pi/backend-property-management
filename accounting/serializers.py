from rest_framework import serializers

from authentication.serializers import UserSerializer
from core.serializers import ModifiedByAbstractSerializer

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


class InvoiceSerializer(ModifiedByAbstractSerializer):
    slug = serializers.CharField(read_only=True)
    rent_cycle = serializers.CharField(source="lease.get_rent_cycle_display", read_only=True)
    total_charges_amount = serializers.CharField(read_only=True)
    charges_and_rent = serializers.CharField(read_only=True)
    is_late_fee_applicable = serializers.BooleanField(read_only=True)
    number_of_days_late = serializers.IntegerField(read_only=True)
    late_fee = serializers.CharField(read_only=True)
    payable_late_fee = serializers.CharField(read_only=True)
    payable_amount = serializers.CharField(read_only=True)
    tenant_first_name = serializers.CharField(source="lease.primary_tenant.first_name", read_only=True)
    tenant_last_name = serializers.CharField(source="lease.primary_tenant.last_name", read_only=True)

    class Meta:
        model = Invoice
        fields = (
            "id",
            "slug",
            "business_information",
            "lease",
            "parent_property",
            "unit",
            "created_at",
            "interval_start_date",
            "interval_end_date",
            "due_date",
            "rent_amount",
            "payed_at",
            "payed_late_fee",
            "status",
            "get_status_display",
            "rent_cycle",
            "total_charges_amount",
            "charges_and_rent",
            "is_late_fee_applicable",
            "number_of_days_late",
            "late_fee",
            "payable_late_fee",
            "payable_amount",
            "arrears_amount",
            "arrear_of",
            "total_paid_amount",
            "payment",
            "tenant_first_name",
            "tenant_last_name",
        )
        read_only_fields = (
            "id",
            "slug",
            "business_information",
            "lease",
            "parent_property",
            "unit",
            "created_at",
            "interval_start_date",
            "interval_end_date",
            "due_date",
            "rent_amount",
            "payed_at",
            "payed_late_fee",
            "get_status_display",
            "rent_cycle",
            "total_charges_amount",
            "charges_and_rent",
            "is_late_fee_applicable",
            "number_of_days_late",
            "late_fee",
            "payable_late_fee",
            "payable_amount",
            "arrears_amount",
            "arrear_of",
            "total_paid_amount",
            "payment",
            "tenant_first_name",
            "tenant_last_name",
        )


class ChargeSerializer(ModifiedByAbstractSerializer):
    property_name = serializers.CharField(source="parent_property.name", read_only=True)
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    tenant_first_name = serializers.CharField(source="tenant.first_name", read_only=True)
    tenant_last_name = serializers.CharField(source="tenant.last_name", read_only=True)
    slug = serializers.CharField(read_only=True)

    class Meta:
        model = Charge
        fields = (
            "id",
            "slug",
            "title",
            "description",
            "charge_type",
            "get_charge_type_display",
            "status",
            "get_status_display",
            "amount",
            "gl_account",
            "tenant",
            "parent_property",
            "unit",
            "notes",
            "created_at",
            "parent_charge",
            "invoice",
            "property_name",
            "unit_name",
            "tenant_first_name",
            "tenant_last_name",
        )
        read_only_fields = ("id", "parent_charge", "invoice")


class ChargeAttachmentSerializer(ModifiedByAbstractSerializer):
    created_by = UserSerializer(many=False, read_only=True)

    class Meta:
        model = ChargeAttachment
        fields = (
            "id",
            "name",
            "created_by",
            "file",
            "charge",
            "file_type",
            "updated_at",
        )
        read_only_fields = ("id", "created_by")


class AccountSerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = Account
        fields = (
            "id",
            "bank_name",
            "branch_name",
            "branch_code",
            "account_title",
            "account_number",
            "iban",
            "address",
            "description",
            "notes",
        )


class AccountAttachmentSerializer(ModifiedByAbstractSerializer):
    created_by = UserSerializer(many=False, read_only=True)

    class Meta:
        model = AccountAttachment
        fields = (
            "id",
            "name",
            "created_by",
            "file",
            "account",
            "file_type",
            "updated_at",
        )
        read_only_fields = ("id", "created_by")


class PaymentSerializer(ModifiedByAbstractSerializer):
    status = serializers.CharField(source="invoice.status", read_only=True)
    get_status_display = serializers.CharField(source="invoice.get_status_display", read_only=True)
    invoice_slug = serializers.CharField(source="invoice.slug", read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "invoice",
            "amount",
            "payment_method",
            "get_payment_method_display",
            "payment_date",
            "status",
            "get_status_display",
            "remarks",
            "notes",
            "account",
            "created_at",
            "invoice_slug",
        )


class PaymentAttachmentSerializer(ModifiedByAbstractSerializer):
    created_by = UserSerializer(many=False, read_only=True)

    class Meta:
        model = PaymentAttachment
        fields = (
            "id",
            "name",
            "created_by",
            "file",
            "payment",
            "file_type",
            "updated_at",
        )
        read_only_fields = ("id", "created_by")


class GeneralLedgerAccountSerializer(ModifiedByAbstractSerializer):
    account_holder_content_type_name = serializers.CharField(
        source="account_holder_content_type.model", read_only=True
    )

    class Meta:
        model = GeneralLedgerAccount
        fields = (
            "id",
            "account_holder_content_type",
            "account_holder_object_id",
            "account_type",
            "get_account_type_display",
            "sub_account_type",
            "get_sub_account_type_display",
            "created_at",
            "account_holder_content_type_name",
        )


class GeneralLedgerTransactionSerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = GeneralLedgerTransaction
        fields = (
            "id",
            "transaction_type",
            "get_transaction_type_display",
            "description",
            "amount",
            "gl_account",
            "created_at",
        )
