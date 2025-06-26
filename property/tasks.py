from __future__ import absolute_import, unicode_literals

from celery import shared_task  # type: ignore[import]
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F

from .models import Property


@shared_task
def scheduled_rent_increase(property_id: int, rent_increase, rent_increase_type):
    try:
        instance = Property.objects.get(id=property_id)
        units = instance.units.all()
        if rent_increase_type == "percentage":
            rent_increase = F("market_rent") + (F("market_rent") * rent_increase / 100)
            units.update(
                market_rent=rent_increase,
            )
        elif rent_increase_type == "fixed":
            rent_increase = F("market_rent") + rent_increase
            units.update(
                market_rent=rent_increase,
            )
    except ObjectDoesNotExist:
        pass
