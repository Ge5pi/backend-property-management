from django.conf import settings
from django.db import models

from core.models import TimestampedModifiedByAbstractModel


class Subscription(TimestampedModifiedByAbstractModel):
    purchased_by = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="purchased_subscription",
    )

    def __str__(self):
        return str(self.pk)
