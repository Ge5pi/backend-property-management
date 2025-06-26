from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounting.models import (
    GeneralLedgerAccount,
    GeneralLedgerAccountLabelChoices,
    GeneralLedgerAccountTypeChoices,
    GeneralLedgerSubAccountTypeChoices,
)


@receiver(post_save, sender="property.Unit")
def create_unit_general_ledger_accounts(sender, instance, created, **kwargs):
    if created:
        content_type = ContentType.objects.get_for_model(instance)
        GLAccountData = [
            {
                "account_type": GeneralLedgerAccountTypeChoices.ASSET,
                "sub_account_type": GeneralLedgerSubAccountTypeChoices.RECEIVABLES,
                "account_holder_content_type": content_type,
                "account_holder_object_id": instance.id,
            },
            {
                "account_type": GeneralLedgerAccountTypeChoices.ASSET,
                "sub_account_type": GeneralLedgerSubAccountTypeChoices.RECEIVABLES,
                "account_holder_content_type": content_type,
                "account_holder_object_id": instance.id,
                "label": GeneralLedgerAccountLabelChoices.SALES_TAX,
            },
            {
                "account_type": GeneralLedgerAccountTypeChoices.ASSET,
                "sub_account_type": GeneralLedgerSubAccountTypeChoices.INVENTORY,
                "account_holder_content_type": content_type,
                "account_holder_object_id": instance.id,
            },
            {
                "account_type": GeneralLedgerAccountTypeChoices.ASSET,
                "sub_account_type": GeneralLedgerSubAccountTypeChoices.FIXED_ASSETS,
                "account_holder_content_type": content_type,
                "account_holder_object_id": instance.id,
            },
            {
                "account_type": GeneralLedgerAccountTypeChoices.INCOME,
                "sub_account_type": GeneralLedgerSubAccountTypeChoices.DIRECT_INCOME,
                "account_holder_content_type": content_type,
                "account_holder_object_id": instance.id,
            },
            {
                "account_type": GeneralLedgerAccountTypeChoices.INCOME,
                "sub_account_type": GeneralLedgerSubAccountTypeChoices.INDIRECT_INCOME,
                "account_holder_content_type": content_type,
                "account_holder_object_id": instance.id,
            },
            {
                "account_type": GeneralLedgerAccountTypeChoices.EXPENSE,
                "sub_account_type": GeneralLedgerSubAccountTypeChoices.DIRECT_EXPENSE,
                "account_holder_content_type": content_type,
                "account_holder_object_id": instance.id,
            },
            {
                "account_type": GeneralLedgerAccountTypeChoices.EXPENSE,
                "sub_account_type": GeneralLedgerSubAccountTypeChoices.INDIRECT_EXPENSE,
                "account_holder_content_type": content_type,
                "account_holder_object_id": instance.id,
            },
            {
                "account_type": GeneralLedgerAccountTypeChoices.LIABILITY,
                "sub_account_type": GeneralLedgerSubAccountTypeChoices.CURRENT_LIABILITY,
                "account_holder_content_type": content_type,
                "account_holder_object_id": instance.id,
            },
            {
                "account_type": GeneralLedgerAccountTypeChoices.LIABILITY,
                "sub_account_type": GeneralLedgerSubAccountTypeChoices.NON_CURRENT_LIABILITY,
                "account_holder_content_type": content_type,
                "account_holder_object_id": instance.id,
            },
            {
                "account_type": GeneralLedgerAccountTypeChoices.ASSET,
                "sub_account_type": GeneralLedgerSubAccountTypeChoices.RECEIVABLES,
                "account_holder_content_type": content_type,
                "account_holder_object_id": instance.id,
                "label": GeneralLedgerAccountLabelChoices.LATE_FEE,
            },
            {
                "account_type": GeneralLedgerAccountTypeChoices.INCOME,
                "sub_account_type": GeneralLedgerSubAccountTypeChoices.INDIRECT_INCOME,
                "account_holder_content_type": content_type,
                "account_holder_object_id": instance.id,
                "label": GeneralLedgerAccountLabelChoices.LATE_FEE,
            },
            {
                "account_type": GeneralLedgerAccountTypeChoices.ASSET,
                "sub_account_type": GeneralLedgerSubAccountTypeChoices.RECEIVABLES,
                "account_holder_content_type": content_type,
                "account_holder_object_id": instance.id,
                "label": GeneralLedgerAccountLabelChoices.CHARGE,
            },
            {
                "account_type": GeneralLedgerAccountTypeChoices.INCOME,
                "sub_account_type": GeneralLedgerSubAccountTypeChoices.INDIRECT_INCOME,
                "account_holder_content_type": content_type,
                "account_holder_object_id": instance.id,
                "label": GeneralLedgerAccountLabelChoices.CHARGE,
            },
        ]
        GeneralLedgerAccount.objects.bulk_create(
            [GeneralLedgerAccount(**data, subscription=instance.subscription) for data in GLAccountData]
        )
