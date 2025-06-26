import pytest

from authentication.serializers import UserSerializer

from ..models import Charge, Invoice
from ..serializers import (
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


@pytest.mark.django_db
def test_invoice_serializer_read(invoice_factory, payment_factory):
    """
    Testing :py:class:`accounting.serializers.InvoiceSerializer` read
    """
    inv = invoice_factory()
    payment_factory(invoice=inv)
    instance = Invoice.objects.annotate_data().annotate_slug().get()
    serializer = InvoiceSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["business_information"] == instance.business_information.id
    assert serializer.data["lease"] == instance.lease.id
    assert serializer.data["parent_property"] == instance.parent_property.id
    assert serializer.data["unit"] == instance.unit.id
    assert serializer.data["interval_start_date"] == str(instance.interval_start_date)
    assert serializer.data["interval_end_date"] == str(instance.interval_end_date)
    assert serializer.data["due_date"] == str(instance.due_date)
    assert serializer.data["rent_amount"] == str(instance.rent_amount)
    assert serializer.data["payed_at"] == str(instance.payed_at)
    assert serializer.data["payed_late_fee"] == str(instance.payed_late_fee)
    assert serializer.data["status"] == instance.status
    assert serializer.data["get_status_display"] == instance.get_status_display()
    assert serializer.data["rent_cycle"] == instance.lease.get_rent_cycle_display()
    assert serializer.data["total_charges_amount"] == str(instance.total_charges_amount)
    assert serializer.data["charges_and_rent"] == str(instance.charges_and_rent)
    assert serializer.data["is_late_fee_applicable"] == instance.is_late_fee_applicable
    assert serializer.data["number_of_days_late"] == instance.number_of_days_late
    assert serializer.data["late_fee"] == instance.late_fee
    assert serializer.data["payable_late_fee"] == instance.payable_late_fee
    assert serializer.data["payable_amount"] == instance.payable_amount
    assert serializer.data["slug"] == instance.slug
    assert serializer.data["arrears_amount"] == str(instance.arrears_amount)
    assert serializer.data["arrear_of"] == instance.arrear_of
    assert serializer.data["total_paid_amount"] == str(instance.total_paid_amount)
    assert serializer.data["payment"] == instance.payment.id
    assert serializer.data["tenant_first_name"] == instance.lease.primary_tenant.first_name
    assert serializer.data["tenant_last_name"] == instance.lease.primary_tenant.last_name
    assert serializer.data.keys() == {
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
    }


@pytest.mark.django_db
def test_charge_serializer_read(charge_factory):
    """
    Testing :py:class:`accounting.serializers.ChargeSerializer` read
    """
    charge_factory()
    instance = Charge.objects.annotate_slug().get()
    serializer = ChargeSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["title"] == instance.title
    assert serializer.data["description"] == instance.description
    assert serializer.data["charge_type"] == instance.charge_type
    assert serializer.data["get_charge_type_display"] == instance.get_charge_type_display()
    assert serializer.data["status"] == instance.status
    assert serializer.data["get_status_display"] == instance.get_status_display()
    assert serializer.data["amount"] == str(instance.amount)
    assert serializer.data["gl_account"] == instance.gl_account
    assert serializer.data["tenant"] == instance.tenant.id
    assert serializer.data["parent_property"] == instance.parent_property.id
    assert serializer.data["unit"] == instance.unit.id
    assert serializer.data["notes"] == instance.notes
    assert serializer.data["created_at"] is not None
    assert serializer.data["parent_charge"] == instance.parent_charge
    assert serializer.data["invoice"] == instance.invoice.id
    assert serializer.data["property_name"] == instance.parent_property.name
    assert serializer.data["unit_name"] == instance.unit.name
    assert serializer.data["tenant_first_name"] == instance.tenant.first_name
    assert serializer.data["tenant_last_name"] == instance.tenant.last_name
    assert serializer.data.keys() == {
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
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "title": ["This field is required."],
                "description": ["This field is required."],
                "charge_type": ["This field is required."],
                "amount": ["This field is required."],
                "gl_account": ["This field is required."],
                "tenant": ["This field is required."],
                "parent_property": ["This field is required."],
                "unit": ["This field is required."],
                "notes": ["This field is required."],
            },
            False,
        ),
        (
            {
                "status": "UNPAID",
                "title": "Chance focus floor provide reach good writer. Drive watch say consumer business out test",
                "description": "Defense save necessary at still.",
                "charge_type": "ONE_TIME",
                "amount": "848.35",
                "gl_account": "92392872.",
                "notes": "Language church surface really go. Offer wonder teacher turn evidence concern occur.",
            },
            {
                "title": "Chance focus floor provide reach good writer. Drive watch say consumer business out test",
                "description": "Defense save necessary at still.",
                "charge_type": "ONE_TIME",
                "status": "UNPAID",
                "amount": "848.35",
                "gl_account": "92392872.",
                "notes": "Language church surface really go. Offer wonder teacher turn evidence concern occur.",
                "parent_charge": None,
                "invoice": None,
                "property_name": "Test Property",
                "unit_name": "Test Unit",
                "tenant_first_name": "John",
                "tenant_last_name": "Doe",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_charges_serializer_write(
    data,
    response,
    is_valid,
    tenant_factory,
    property_factory,
    unit_factory,
    applicant_factory,
    rental_application_factory,
    lease_factory,
):
    """
    Testing :py:class:`accounting.serializers.ChargeSerializer` write
    """
    prop = property_factory(name="Test Property")
    unit = unit_factory(name="Test Unit")
    applicant = applicant_factory(first_name="John", last_name="Doe")
    rental_application = rental_application_factory(applicant=applicant)
    lease = lease_factory(rental_application=rental_application)

    if is_valid:
        data["tenant"] = lease.primary_tenant.id
        data["parent_property"] = prop.id
        data["unit"] = unit.id
        response["tenant"] = lease.primary_tenant.id
        response["parent_property"] = prop.id
        response["unit"] = unit.id

    serializer = ChargeSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_charge_attachment_serializer_read(charge_factory, charge_attachment_factory, user_factory):
    """
    Testing :py:class:`communication.serializers.ChargeAttachmentSerializer` read
    """
    charge = charge_factory()
    user = user_factory()
    instance = charge_attachment_factory(charge=charge, created_by=user)

    serializer = ChargeAttachmentSerializer(instance)

    assert serializer.data["charge"] == charge.id
    assert serializer.data["created_by"] == UserSerializer(instance.created_by).data
    assert serializer.data["file"] == instance.file
    assert serializer.data["name"] == instance.name
    assert serializer.data["file_type"] == instance.file_type
    assert serializer.data["updated_at"] is not None
    assert serializer.data.keys() == {
        "id",
        "name",
        "created_by",
        "file",
        "charge",
        "file_type",
        "updated_at",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "file": ["This field is required."],
                "charge": ["This field is required."],
                "file_type": ["This field is required."],
            },
            False,
        ),
        (
            {
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            {
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_charge_attachment_serializer_write(charge_factory, data, response, is_valid):
    """
    Testing :py:class:`communication.serializers.ChargeAttachmentSerializer` write
    """

    charge = charge_factory()

    if is_valid:
        data["charge"] = charge.id
        response["charge"] = charge.id

    serializer = ChargeAttachmentSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_account_serializer_read(account_factory):
    """
    Testing :py:class:`accounting.serializers.AccountSerializer` read
    """
    instance = account_factory()
    serializer = AccountSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["bank_name"] == instance.bank_name
    assert serializer.data["branch_name"] == instance.branch_name
    assert serializer.data["branch_code"] == str(instance.branch_code)
    assert serializer.data["account_title"] == instance.account_title
    assert serializer.data["account_number"] == str(instance.account_number)
    assert serializer.data["iban"] == instance.iban
    assert serializer.data["address"] == instance.address
    assert serializer.data["description"] == instance.description
    assert serializer.data["notes"] == instance.notes
    assert serializer.data.keys() == {
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
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "bank_name": ["This field is required."],
                "branch_name": ["This field is required."],
                "branch_code": ["This field is required."],
                "account_title": ["This field is required."],
                "account_number": ["This field is required."],
                "iban": ["This field is required."],
            },
            False,
        ),
        (
            {
                "bank_name": "Bank of America",
                "branch_name": "New York",
                "branch_code": "123456",
                "account_title": "James Ramirez",
                "account_number": "1234567890",
                "iban": "1234567890",
                "address": "New York",
                "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "notes": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            },
            {
                "bank_name": "Bank of America",
                "branch_name": "New York",
                "branch_code": "123456",
                "account_title": "James Ramirez",
                "account_number": "1234567890",
                "iban": "1234567890",
                "address": "New York",
                "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "notes": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_account_serializer_write(data, response, is_valid):
    """
    Testing :py:class:`accounting.serializers.AccountSerializer` write
    """
    serializer = AccountSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_account_attachment_serializer_read(account_attachment_factory, user_factory):
    """
    Testing :py:class:`accounting.serializers.AccountAttachmentSerializer` read
    """

    user = user_factory()
    instance = account_attachment_factory(created_by=user)

    serializer = AccountAttachmentSerializer(instance)

    assert serializer.data["account"] == instance.account.id
    assert serializer.data["created_by"] == UserSerializer(instance.created_by).data
    assert serializer.data["file"] == instance.file
    assert serializer.data["name"] == instance.name
    assert serializer.data["file_type"] == instance.file_type
    assert serializer.data["updated_at"] is not None
    assert serializer.data.keys() == {
        "id",
        "name",
        "created_by",
        "file",
        "account",
        "file_type",
        "updated_at",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "file": ["This field is required."],
                "account": ["This field is required."],
                "file_type": ["This field is required."],
            },
            False,
        ),
        (
            {
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            {
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_account_attachment_serializer_write(account_factory, data, response, is_valid):
    """
    Testing :py:class:`accounting.serializers.AccountAttachmentSerializer` write
    """
    account = account_factory()

    if is_valid:
        data["account"] = account.id
        response["account"] = account.id

    serializer = AccountAttachmentSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_payment_serializer_read(payment_factory):
    """
    Testing :py:class:`accounting.serializers.PaymentSerializer` read
    """
    instance = payment_factory()
    serializer = PaymentSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["invoice"] == instance.invoice.id
    assert serializer.data["amount"] == str(instance.amount)
    assert serializer.data["payment_method"] == instance.payment_method
    assert serializer.data["get_payment_method_display"] == instance.get_payment_method_display()
    assert serializer.data["payment_date"] == str(instance.payment_date)
    assert serializer.data["status"] == instance.invoice.status
    assert serializer.data["get_status_display"] == instance.invoice.get_status_display()
    assert serializer.data["remarks"] == instance.remarks
    assert serializer.data["account"] == instance.account.id
    assert serializer.data["created_at"] is not None
    assert serializer.data["notes"] == instance.notes
    assert serializer.data.keys() == {
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
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "invoice": ["This field is required."],
                "amount": ["This field is required."],
                "payment_method": ["This field is required."],
                "payment_date": ["This field is required."],
            },
            False,
        ),
        (
            {
                "invoice": 1,
                "amount": "100.00",
                "payment_method": "BANK_TRANSFER",
                "payment_date": "2023-01-01",
                "remarks": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "account": 1,
                "notes": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            },
            {
                "invoice": 1,
                "amount": "100.00",
                "payment_method": "BANK_TRANSFER",
                "payment_date": "2023-01-01",
                "remarks": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "account": 1,
                "status": "UNPAID",
                "get_status_display": "Not Paid",
                "notes": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_payment_serializer_write(data, response, is_valid, invoice_factory, account_factory):
    """
    Testing :py:class:`accounting.serializers.PaymentSerializer` write
    """

    invoice = invoice_factory()
    account = account_factory()

    if is_valid:
        data["invoice"] = invoice.id
        data["account"] = account.id
        response["invoice"] = invoice.id
        response["account"] = account.id

    serializer = PaymentSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_payment_attachment_serializer_read(payment_attachment_factory, user_factory):
    """
    Testing :py:class:`accounting.serializers.PaymentAttachmentSerializer` read
    """

    user = user_factory()
    instance = payment_attachment_factory(created_by=user)

    serializer = PaymentAttachmentSerializer(instance)

    assert serializer.data["payment"] == instance.payment.id
    assert serializer.data["created_by"] == UserSerializer(instance.created_by).data
    assert serializer.data["file"] == instance.file
    assert serializer.data["name"] == instance.name
    assert serializer.data["file_type"] == instance.file_type
    assert serializer.data["updated_at"] is not None
    assert serializer.data.keys() == {
        "id",
        "name",
        "created_by",
        "file",
        "payment",
        "file_type",
        "updated_at",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "file": ["This field is required."],
                "payment": ["This field is required."],
                "file_type": ["This field is required."],
            },
            False,
        ),
        (
            {
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            {
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_payment_attachment_serializer_write(payment_factory, data, response, is_valid):
    """
    Testing :py:class:`accounting.serializers.PaymentAttachmentSerializer` write
    """
    payment = payment_factory()

    if is_valid:
        data["payment"] = payment.id
        response["payment"] = payment.id

    serializer = PaymentAttachmentSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_general_ledger_account_serializer_read(general_ledger_account_factory):
    """
    Testing :py:class:`accounting.serializers.GeneralLedgerAccountSerializer` read
    """
    instance = general_ledger_account_factory()
    serializer = GeneralLedgerAccountSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["account_type"] == instance.account_type
    assert serializer.data["get_account_type_display"] == instance.get_account_type_display()
    assert serializer.data["sub_account_type"] == instance.sub_account_type
    assert serializer.data["get_sub_account_type_display"] == instance.get_sub_account_type_display()
    assert serializer.data["account_holder_content_type"] == instance.account_holder_content_type.id
    assert serializer.data["account_holder_object_id"] == instance.account_holder_object_id
    assert serializer.data["created_at"] is not None
    assert serializer.data["account_holder_content_type_name"] == instance.account_holder_content_type.name
    assert serializer.data.keys() == {
        "id",
        "account_holder_content_type",
        "account_holder_object_id",
        "account_type",
        "get_account_type_display",
        "sub_account_type",
        "get_sub_account_type_display",
        "created_at",
        "account_holder_content_type_name",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "account_type": ["This field is required."],
                "sub_account_type": ["This field is required."],
                "account_holder_content_type": ["This field is required."],
                "account_holder_object_id": ["This field is required."],
            },
            False,
        ),
        (
            {
                "account_type": "ASSET",
                "sub_account_type": "CASH_OR_BANK",
                "account_holder_object_id": 1,
            },
            {
                "account_type": "ASSET",
                "sub_account_type": "CASH_OR_BANK",
                "account_holder_object_id": 1,
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_general_ledger_account_serializer_write(data, response, is_valid, general_ledger_account_factory):
    """
    Testing :py:class:`accounting.serializers.GeneralLedgerAccountSerializer` write
    """
    serializer = GeneralLedgerAccountSerializer(data=data)
    gl_account = general_ledger_account_factory()

    if is_valid:
        data["account_holder_content_type"] = gl_account.account_holder_content_type.id
        response["account_holder_content_type"] = gl_account.account_holder_content_type.id
        response["account_holder_content_type_name"] = gl_account.account_holder_content_type.name

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_general_ledger_transaction_serializer_read(general_ledger_transaction_factory):
    """
    Testing :py:class:`accounting.serializers.GeneralLedgerTransactionSerializer` read
    """

    instance = general_ledger_transaction_factory()
    serializer = GeneralLedgerTransactionSerializer(instance)

    assert serializer.data["id"] == instance.id
    assert serializer.data["transaction_type"] == instance.transaction_type
    assert serializer.data["get_transaction_type_display"] == instance.get_transaction_type_display()
    assert serializer.data["amount"] == str(instance.amount)
    assert serializer.data["description"] == instance.description
    assert serializer.data["gl_account"] == instance.gl_account.id
    assert serializer.data.keys() == {
        "id",
        "transaction_type",
        "get_transaction_type_display",
        "description",
        "amount",
        "gl_account",
        "created_at",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "transaction_type": ["This field is required."],
                "amount": ["This field is required."],
                "description": ["This field is required."],
                "gl_account": ["This field is required."],
            },
            False,
        ),
        (
            {
                "transaction_type": "DEBIT",
                "amount": "100.00",
                "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            },
            {
                "transaction_type": "DEBIT",
                "amount": "100.00",
                "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_general_ledger_transaction_serializer_write(data, response, is_valid, general_ledger_account_factory):
    """
    Testing :py:class:`accounting.serializers.GeneralLedgerTransactionSerializer` write
    """
    gl_account = general_ledger_account_factory()

    if is_valid:
        data["gl_account"] = gl_account.id
        response["gl_account"] = gl_account.id

    serializer = GeneralLedgerTransactionSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response
