from __future__ import absolute_import, unicode_literals

import os

from celery import Celery  # type: ignore[import]
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "property_management.settings")

app = Celery("property_management", broker=settings.CELERY_BROKER_URL)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
