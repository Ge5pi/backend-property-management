import factory  # type: ignore[import]

from core.tests import BaseAttachmentFactory, SubscriptionAbstractFactory


class InvoiceFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "accounting.Invoice"

    business_information = factory.SubFactory("system_preferences.tests.factories.BusinessInformationFactory")
    lease = factory.SubFactory("lease.tests.factories.LeaseFactory")
    parent_property = factory.SubFactory("property.tests.factories.PropertyFactory")
    unit = factory.SubFactory("property.tests.factories.UnitFactory")
    interval_start_date = factory.Faker("date")
    interval_end_date = factory.Faker("date")
    due_date = factory.Faker("date")
    rent_amount = factory.Faker("pydecimal", min_value=0, max_value=1000, right_digits=2)
    payed_at = factory.Faker("date")
    payed_late_fee = factory.Faker("pydecimal", min_value=0, max_value=1000, right_digits=2)
    status = "UNPAID"
    arrears_amount = factory.Faker("pydecimal", min_value=0, max_value=1000, right_digits=2)
    total_paid_amount = factory.Faker("pydecimal", min_value=0, max_value=1000, right_digits=2)


class ChargeFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "accounting.Charge"

    title = factory.Faker("text", max_nb_chars=255)
    description = factory.Faker("text")
    charge_type = "ONE_TIME"
    status = "UNPAID"
    amount = factory.Faker("pydecimal", min_value=0, max_value=1000, right_digits=2)
    gl_account = factory.Faker("text", max_nb_chars=255)
    tenant = factory.SubFactory("people.tests.factories.TenantFactory")
    parent_property = factory.SubFactory("property.tests.factories.PropertyFactory")
    unit = factory.SubFactory("property.tests.factories.UnitFactory")
    notes = factory.Faker("text")
    invoice = factory.SubFactory("accounting.tests.factories.InvoiceFactory")


class ChargeAttachmentFactory(BaseAttachmentFactory):
    class Meta:
        model = "accounting.ChargeAttachment"

    charge = factory.SubFactory("accounting.tests.factories.ChargeFactory")


class AccountFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "accounting.Account"

    bank_name = factory.Faker("company")
    branch_name = factory.Faker("city")
    branch_code = factory.Faker("random_number", digits=6)
    account_title = factory.Faker("name")
    account_number = factory.Faker("random_number", digits=10)
    iban = factory.Faker("iban")
    address = factory.Faker("address")
    description = factory.Faker("text")
    notes = factory.Faker("text")


class AccountAttachmentFactory(BaseAttachmentFactory):
    class Meta:
        model = "accounting.AccountAttachment"

    account = factory.SubFactory("accounting.tests.factories.AccountFactory")


class PaymentFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "accounting.Payment"

    invoice = factory.SubFactory("accounting.tests.factories.InvoiceFactory")
    amount = factory.Faker("pydecimal", min_value=0, max_value=1000, right_digits=2)
    payment_method = "BANK_TRANSFER"
    payment_date = factory.Faker("date")
    remarks = factory.Faker("text")
    account = factory.SubFactory("accounting.tests.factories.AccountFactory")
    notes = factory.Faker("text")


class PaymentAttachmentFactory(BaseAttachmentFactory):
    class Meta:
        model = "accounting.PaymentAttachment"

    payment = factory.SubFactory("accounting.tests.factories.PaymentFactory")


class GeneralLedgerAccountFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "accounting.GeneralLedgerAccount"

    account_type = "ASSET"
    sub_account_type = "CASH_OR_BANK"
    account_holder_content_type = factory.SubFactory("core.tests.ContentTypeFactory")
    account_holder_object_id = factory.Faker("random_number", digits=3)


class GeneralLedgerTransactionFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "accounting.GeneralLedgerTransaction"

    transaction_type = "DEBIT"
    amount = factory.Faker("pydecimal", min_value=0, max_value=1000, right_digits=2)
    description = factory.Faker("text")
    gl_account = factory.SubFactory("accounting.tests.factories.GeneralLedgerAccountFactory")
