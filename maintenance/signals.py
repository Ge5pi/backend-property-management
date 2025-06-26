from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounting.models import GeneralLedgerAccount, GeneralLedgerAccountTypeChoices, GeneralLedgerSubAccountTypeChoices


@receiver(post_save, sender="maintenance.Project")
def create_project_general_ledger_accounts(sender, instance, created, **kwargs):
    if created:
        content_type = ContentType.objects.get_for_model(instance)
        data = {
            "account_type": GeneralLedgerAccountTypeChoices.EXPENSE,
            "sub_account_type": GeneralLedgerSubAccountTypeChoices.INDIRECT_EXPENSE,
            "account_holder_content_type": content_type,
            "account_holder_object_id": instance.id,
        }
        GeneralLedgerAccount.objects.create(**data, subscription=instance.subscription)


@receiver(post_save, sender="maintenance.Inventory")
def create_inventory_general_ledger_accounts(sender, instance, created, **kwargs):
    if created:
        content_type = ContentType.objects.get_for_model(instance)
        data = {
            "account_type": GeneralLedgerAccountTypeChoices.ASSET,
            "sub_account_type": GeneralLedgerSubAccountTypeChoices.INVENTORY,
            "account_holder_content_type": content_type,
            "account_holder_object_id": instance.id,
        }
        GeneralLedgerAccount.objects.create(**data, subscription=instance.subscription)
