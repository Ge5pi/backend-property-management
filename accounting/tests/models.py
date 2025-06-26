from datetime import datetime
from decimal import Decimal

import pytest
from pytest import approx

from accounting.models import (
    Account,
    AccountAttachment,
    Charge,
    ChargeAttachment,
    ChargeTypeChoices,
    GeneralLedgerAccount,
    GeneralLedgerTransaction,
    Invoice,
    Payment,
    PaymentAttachment,
    PaymentStatusChoices,
)
from core.models import BaseAttachment, CommonInfoAbstractModel


@pytest.mark.django_db
def test_invoice(
    invoice_factory,
    business_information_factory,
    lease_factory,
    property_factory,
    unit_factory,
):
    """
    Testing :py:class:`accounting.models.Invoice` model with factory
    """
    business_information = business_information_factory()
    lease = lease_factory()
    parent_property = property_factory()
    unit = unit_factory()
    arrear_invoice = invoice_factory()

    invoice = invoice_factory(
        business_information=business_information,
        lease=lease,
        parent_property=parent_property,
        unit=unit,
        interval_start_date=datetime(2023, 1, 1),
        interval_end_date=datetime(2023, 1, 1),
        due_date=datetime(2023, 1, 1),
        rent_amount=Decimal("100.00"),
        payed_at=datetime(2023, 1, 1),
        payed_late_fee=Decimal("10.00"),
        status=PaymentStatusChoices.PAID_NOT_VERIFIED,
        arrears_amount=Decimal("0.00"),
        arrear_of=arrear_invoice,
        total_paid_amount=Decimal("90.00"),
    )

    invoices = Invoice.objects.all()

    assert invoices.count() == 2
    assert invoice.pk is not None
    assert invoice.business_information == business_information
    assert invoice.lease == lease
    assert invoice.parent_property == parent_property
    assert invoice.unit == unit
    assert invoice.interval_start_date == datetime(2023, 1, 1)
    assert invoice.interval_end_date == datetime(2023, 1, 1)
    assert invoice.interval_start_date == datetime(2023, 1, 1)
    assert invoice.due_date == datetime(2023, 1, 1)
    assert invoice.rent_amount == approx(Decimal("100.00"))
    assert invoice.payed_at == datetime(2023, 1, 1)
    assert invoice.payed_late_fee == approx(Decimal("10.00"))
    assert invoice.status == PaymentStatusChoices.PAID_NOT_VERIFIED
    assert invoice.arrears_amount == approx(Decimal("0.00"))
    assert invoice.arrear_of == arrear_invoice
    assert invoice.total_paid_amount == approx(Decimal("90.00"))
    assert str(invoice) == unit.name
    assert issubclass(Invoice, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_charge(charge_factory, tenant_factory, property_factory, unit_factory):
    """
    Testing :py:class:`accounting.models.Charge` model with factory
    """
    tenant = tenant_factory()
    parent_property = property_factory()
    unit = unit_factory()

    charge = charge_factory(
        title="James Ramirez",
        description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        charge_type=ChargeTypeChoices.ONE_TIME,
        status=PaymentStatusChoices.UNPAID,
        amount=Decimal("100.00"),
        gl_account="test",
        tenant=tenant,
        parent_property=parent_property,
        unit=unit,
        notes="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    )

    charges = Charge.objects.all()

    assert charges.count() == 1
    assert charge.pk is not None
    assert charge.title == "James Ramirez"
    assert charge.description == "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    assert charge.charge_type == ChargeTypeChoices.ONE_TIME
    assert charge.status == PaymentStatusChoices.UNPAID
    assert charge.amount == approx(Decimal("100.00"))
    assert charge.gl_account == "test"
    assert charge.tenant == tenant
    assert charge.parent_property == parent_property
    assert charge.unit == unit
    assert charge.notes == "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    assert str(charge) == "James Ramirez"
    assert issubclass(Charge, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_charge_attachment(charge_attachment_factory, charge_factory):
    """
    Testing :py:class:`accounting.models.ChargeAttachment` model with factory
    """
    charge = charge_factory()
    charge_attachment = charge_attachment_factory(
        name="Property Agreement", file="test.pdf", file_type="pdf", charge=charge
    )

    charge_attachments = ChargeAttachment.objects.all()

    assert charge_attachments.count() == 1
    assert charge_attachment.pk is not None
    assert charge_attachment.name == "Property Agreement"
    assert charge_attachment.file == "test.pdf"
    assert charge_attachment.file_type == "pdf"
    assert charge_attachment.charge == charge
    assert str(charge_attachment) == "Property Agreement"
    assert issubclass(ChargeAttachment, CommonInfoAbstractModel)
    assert issubclass(ChargeAttachment, BaseAttachment)


@pytest.mark.django_db
def test_account(account_factory):
    """
    Testing :py:class:`accounting.models.Account` model with factory
    """
    account = account_factory(
        bank_name="Bank of America",
        branch_name="New York",
        branch_code="123456",
        account_title="James Ramirez",
        account_number="1234567890",
        iban="1234567890",
        address="New York",
        description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        notes="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    )

    accounts = Account.objects.all()

    assert accounts.count() == 1
    assert account.pk is not None
    assert account.bank_name == "Bank of America"
    assert account.branch_name == "New York"
    assert account.branch_code == "123456"
    assert account.account_title == "James Ramirez"
    assert account.account_number == "1234567890"
    assert account.iban == "1234567890"
    assert account.address == "New York"
    assert account.description == "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    assert account.notes == "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    assert str(account) == "James Ramirez"
    assert issubclass(Account, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_account_attachment(account_attachment_factory, account_factory):
    """
    Testing :py:class:`accounting.models.AccountAttachment` model with factory
    """

    account = account_factory()
    account_attachment = account_attachment_factory(
        name="Property Agreement", file="test.pdf", file_type="pdf", account=account
    )

    account_attachments = AccountAttachment.objects.all()

    assert account_attachments.count() == 1
    assert account_attachment.pk is not None
    assert account_attachment.name == "Property Agreement"
    assert account_attachment.file == "test.pdf"
    assert account_attachment.file_type == "pdf"
    assert account_attachment.account == account
    assert str(account_attachment) == "Property Agreement"
    assert issubclass(AccountAttachment, CommonInfoAbstractModel)
    assert issubclass(AccountAttachment, BaseAttachment)


@pytest.mark.django_db
def test_payment(payment_factory, invoice_factory, account_factory):
    """
    Testing :py:class:`accounting.models.Payment` model with factory
    """

    invoice = invoice_factory()
    account = account_factory()
    payment = payment_factory(
        invoice=invoice,
        amount=Decimal("100.00"),
        payment_method="BANK_TRANSFER",
        payment_date=datetime(2023, 1, 1),
        remarks="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        account=account,
        notes="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    )

    payments = Payment.objects.all()

    assert payments.count() == 1
    assert payment.pk is not None
    assert payment.invoice == invoice
    assert payment.amount == approx(Decimal("100.00"))
    assert payment.payment_method == "BANK_TRANSFER"
    assert payment.payment_date == datetime(2023, 1, 1)
    assert payment.remarks == "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    assert payment.account == account
    assert payment.notes == "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    assert str(payment) == str(invoice) + " - " + str(Decimal("100.00"))
    assert issubclass(Payment, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_payment_attachment(payment_attachment_factory, payment_factory):
    """
    Testing :py:class:`accounting.models.PaymentAttachment` model with factory
    """

    payment = payment_factory()
    payment_attachment = payment_attachment_factory(
        name="Property Agreement", file="test.pdf", file_type="pdf", payment=payment
    )

    payment_attachments = PaymentAttachment.objects.all()

    assert payment_attachments.count() == 1
    assert payment_attachment.pk is not None
    assert payment_attachment.name == "Property Agreement"
    assert payment_attachment.file == "test.pdf"
    assert payment_attachment.file_type == "pdf"
    assert payment_attachment.payment == payment
    assert str(payment_attachment) == "Property Agreement"
    assert issubclass(PaymentAttachment, CommonInfoAbstractModel)
    assert issubclass(PaymentAttachment, BaseAttachment)


@pytest.mark.django_db
def test_general_ledger_account(general_ledger_account_factory, content_type_factory):
    """
    Testing :py:class:`accounting.models.GeneralLedgerAccount` model with factory
    """

    content_type = content_type_factory()
    general_ledger_account = general_ledger_account_factory(
        account_type="ASSET",
        sub_account_type="CASH_OR_BANK",
        account_holder_content_type=content_type,
        account_holder_object_id=1234567890,
    )

    general_ledger_accounts = GeneralLedgerAccount.objects.all()

    assert general_ledger_accounts.count() == 1
    assert general_ledger_account.pk is not None
    assert general_ledger_account.account_type == "ASSET"
    assert general_ledger_account.sub_account_type == "CASH_OR_BANK"
    assert general_ledger_account.account_holder_content_type == content_type
    assert general_ledger_account.account_holder_object_id == 1234567890
    assert str(general_ledger_account) == f"{str(content_type)} #1234567890"
    assert issubclass(GeneralLedgerAccount, CommonInfoAbstractModel)


@pytest.mark.django_db
def test_general_ledger_transaction(general_ledger_transaction_factory, general_ledger_account_factory):
    """
    Testing :py:class:`accounting.models.GeneralLedgerTransaction` model with factory
    """

    gl_account = general_ledger_account_factory()
    general_ledger_transaction = general_ledger_transaction_factory(
        transaction_type="DEBIT",
        amount=Decimal("100.00"),
        description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        gl_account=gl_account,
    )

    general_ledger_transactions = GeneralLedgerTransaction.objects.all()

    assert general_ledger_transactions.count() == 1
    assert general_ledger_transaction.pk is not None
    assert general_ledger_transaction.transaction_type == "DEBIT"
    assert general_ledger_transaction.amount == approx(Decimal("100.00"))
    assert general_ledger_transaction.description == "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    assert general_ledger_transaction.gl_account == gl_account
    assert str(general_ledger_transaction) == f"{str(gl_account)} - 100.00 - DEBIT"
    assert issubclass(GeneralLedgerTransaction, CommonInfoAbstractModel)
