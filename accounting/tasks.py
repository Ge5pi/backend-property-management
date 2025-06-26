from celery import shared_task  # type: ignore[import]
from django.core import management


@shared_task
def create_invoices_of_units_task():
    management.call_command("create_invoices_of_units")
