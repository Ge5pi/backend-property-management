from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from core.models import BaseAttachment, CommonInfoAbstractModel

from .managers import ChargeManager, InvoiceManager


class PaymentStatusChoices(models.TextChoices):
    UNPAID = "UNPAID", "Not Paid"
    PAID_NOT_VERIFIED = "NOT_VERIFIED", "Paid / Not Verified"
    PAID_VERIFIED = "VERIFIED", "Paid / Verified"
    REJECTED = "REJECTED", "Rejected"


class Invoice(CommonInfoAbstractModel):
    SLUG = "inv"

    business_information = models.ForeignKey(
        "system_preferences.BusinessInformation",
        related_name="invoices",
        on_delete=models.CASCADE,
        null=True,
    )
    lease = models.ForeignKey("lease.Lease", related_name="invoices", on_delete=models.CASCADE)
    parent_property = models.ForeignKey("property.Property", related_name="invoices", on_delete=models.CASCADE)
    unit = models.ForeignKey("property.Unit", related_name="invoices", on_delete=models.CASCADE)
    interval_start_date = models.DateField()
    interval_end_date = models.DateField()
    due_date = models.DateField()
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payed_at = models.DateField(blank=True, null=True)
    payed_late_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=PaymentStatusChoices.choices,
        default=PaymentStatusChoices.UNPAID,
    )
    arrears_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    arrear_of = models.ForeignKey("self", related_name="arrears", on_delete=models.SET_NULL, blank=True, null=True)
    total_paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    objects = InvoiceManager()

    def __str__(self):
        return self.unit.name


class ChargeTypeChoices(models.TextChoices):
    ONE_TIME = "ONE_TIME", "One Time"
    RECURRING = "RECURRING", "Recurring"


class Charge(CommonInfoAbstractModel):
    SLUG = "chg"
    title = models.CharField(max_length=255)
    description = models.TextField()
    charge_type = models.CharField(max_length=20, choices=ChargeTypeChoices.choices)
    status = models.CharField(
        max_length=20,
        choices=PaymentStatusChoices.choices,
        default=PaymentStatusChoices.UNPAID,
        blank=True,
        null=True,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    gl_account = models.CharField(max_length=255)
    tenant = models.ForeignKey("people.Tenant", related_name="charges", on_delete=models.CASCADE)
    parent_property = models.ForeignKey("property.Property", related_name="charges", on_delete=models.CASCADE)
    unit = models.ForeignKey("property.Unit", related_name="charges", on_delete=models.CASCADE)
    notes = models.TextField()
    parent_charge = models.ForeignKey(
        "self",
        related_name="one_time_charges",
        on_delete=models.CASCADE,
        limit_choices_to={"charge_type": "RECURRING"},
        blank=True,
        null=True,
    )
    invoice = models.ForeignKey(Invoice, related_name="charges", on_delete=models.CASCADE, blank=True, null=True)

    objects = ChargeManager()

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(models.Q(charge_type=ChargeTypeChoices.RECURRING) & models.Q(status__isnull=True))
                | (models.Q(charge_type=ChargeTypeChoices.ONE_TIME) & models.Q(status__isnull=False)),
                name="no_status_for_recurring",
                violation_error_message="Recurring Charge cannot have status and vise versa.",
            )
        ]

    def __str__(self):
        return self.title


class ChargeAttachment(BaseAttachment, CommonInfoAbstractModel):
    charge = models.ForeignKey(Charge, related_name="attachments", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Account(CommonInfoAbstractModel):
    bank_name = models.CharField(max_length=100)
    branch_name = models.CharField(max_length=100)
    branch_code = models.CharField(max_length=50)
    account_title = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    iban = models.CharField(max_length=50)
    address = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.account_title


class AccountAttachment(BaseAttachment, CommonInfoAbstractModel):
    account = models.ForeignKey(Account, related_name="attachments", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class PaymentMethods(models.TextChoices):
    BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"
    CARD = "CARD", "Card"


class Payment(CommonInfoAbstractModel):
    invoice = models.OneToOneField(Invoice, related_name="payment", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PaymentMethods.choices)
    payment_date = models.DateField()
    remarks = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    account = models.ForeignKey(Account, related_name="payments", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.invoice} - {self.amount}"

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(models.Q(payment_method=PaymentMethods.BANK_TRANSFER) & models.Q(account__isnull=False))
                | (models.Q(payment_method=PaymentMethods.CARD) & models.Q(account__isnull=True)),
                name="bank_transfer_requires_account",
                violation_error_message="Bank Transfer requires Account",
            )
        ]


class PaymentAttachment(BaseAttachment, CommonInfoAbstractModel):
    payment = models.ForeignKey(Payment, related_name="attachments", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class GeneralLedgerAccountTypeChoices(models.TextChoices):
    ASSET = "ASSET", "Asset"
    LIABILITY = "LIABILITY", "Liability"
    EQUITY = "EQUITY", "Equity"
    INCOME = "INCOME", "Income"
    EXPENSE = "EXPENSE", "Expense"


class GeneralLedgerSubAccountTypeChoices(models.TextChoices):
    # Asset
    RECEIVABLES = "RECEIVABLES", "Receivables"
    INVENTORY = "INVENTORY", "Inventory"
    FIXED_ASSETS = "FIXED_ASSETS", "Fixed Assets"
    CASH_OR_BANK = "CASH_OR_BANK", "Cash / Bank"
    # Liability
    CURRENT_LIABILITY = "CURRENT_LIABILITY", "Current Liability"
    NON_CURRENT_LIABILITY = "NON_CURRENT_LIABILITY", "Non Current Liability"
    # Equity
    DRAWINGS = "DRAWINGS", "Drawings"
    # Income
    DIRECT_INCOME = "DIRECT_INCOME", "Direct Income"
    INDIRECT_INCOME = "INDIRECT_INCOME", "Indirect Income"
    # Expense
    DIRECT_EXPENSE = "DIRECT_EXPENSE", "Direct Expense"
    INDIRECT_EXPENSE = "INDIRECT_EXPENSE", "Indirect Expense"


class GeneralLedgerAccountLabelChoices(models.TextChoices):
    SALES_TAX = "SALES_TAX", "Sales Tax"
    LATE_FEE = "LATE_FEE", "Late Fee"
    CHARGE = "CHARGE", "Charge"
    PROJECT = "PROJECT", "Project"


class GeneralLedgerTransactionTypeChoices(models.TextChoices):
    DEBIT = "DEBIT", "Debit"
    CREDIT = "CREDIT", "Credit"


class GeneralLedgerAccount(CommonInfoAbstractModel):
    account_type = models.CharField(max_length=25, choices=GeneralLedgerAccountTypeChoices.choices)
    sub_account_type = models.CharField(max_length=25, choices=GeneralLedgerSubAccountTypeChoices.choices)
    account_holder_content_type = models.ForeignKey(
        "contenttypes.ContentType", related_name="general_ledger_accounts", on_delete=models.CASCADE
    )
    account_holder_object_id = models.PositiveIntegerField()
    label = models.CharField(max_length=25, choices=GeneralLedgerAccountLabelChoices.choices, blank=True, null=True)

    def __str__(self):
        return f"{self.account_holder_content_type} #{self.account_holder_object_id}"

    class Meta:
        unique_together = (
            "account_holder_content_type",
            "account_holder_object_id",
            "account_type",
            "sub_account_type",
            "label",
        )


class GeneralLedgerTransaction(CommonInfoAbstractModel):
    transaction_type = models.CharField(max_length=20, choices=GeneralLedgerTransactionTypeChoices.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    gl_account = models.ForeignKey(GeneralLedgerAccount, related_name="transactions", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.gl_account} - {self.amount} - {self.transaction_type}"


@receiver(pre_save, sender=Charge)
def set_status_null(sender, instance, *args, **kwargs):
    if instance.charge_type == ChargeTypeChoices.RECURRING:
        instance.status = None
