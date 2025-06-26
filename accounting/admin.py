from django.contrib import admin

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


@admin.register(Charge)
class ChargeAdmin(admin.ModelAdmin):
    list_display = ["title", "charge_type", "status", "amount", "created_at"]
    search_fields = ["title", "description"]
    list_filter = ["status", "charge_type"]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["id", "unit", "lease", "status", "rent_amount", "created_at"]
    search_fields = ["unit__name", "lease__tenant__name"]
    list_filter = ["status"]


@admin.register(GeneralLedgerAccount)
class GeneralLedgerAccountAdmin(admin.ModelAdmin):
    list_display = [
        "account_holder_content_type",
        "account_holder_object_id",
        "account_type",
        "sub_account_type",
        "created_at",
    ]
    search_fields = ["account_holder_content_type"]
    list_filter = ["account_holder_content_type", "account_type", "sub_account_type"]


@admin.register(GeneralLedgerTransaction)
class GeneralLedgerTransactionAdmin(admin.ModelAdmin):
    list_display = ["id", "transaction_type", "amount", "created_at"]
    search_fields = ["transaction_type"]
    list_filter = ["transaction_type"]


admin.site.register(ChargeAttachment)
admin.site.register(Payment)
admin.site.register(PaymentAttachment)
admin.site.register(Account)
admin.site.register(AccountAttachment)
