from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseAttachment(models.Model):
    name = models.CharField(max_length=255)
    file = models.CharField(max_length=2000)
    file_type = models.CharField(max_length=255)

    class Meta:
        abstract = True
        ordering = ["-updated_at"]


class ModifiedByAbstractModel(models.Model):
    """
    An abstract model that adds a ``created_by`` and ``modified_by`` fields to a model to log the user who last
    modified or create an object.
    Use :py:func:`apps.core.utils.models.log_who_did` with an object that implements this class and a user
    account to these fields properly.
    """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("created by"),
        related_name="%(app_label)s_%(class)s_created",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("modified by"),
        related_name="%(app_label)s_%(class)s_modified",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        abstract = True


class TimestampedAbstractModel(models.Model):  # # AccountabilityMixin
    """
    An abstract model that adds a ``created_at`` and ``modified_at`` field to a model that inherits this class.
    The fields are automatically set whenever an object's ``save`` function is called. See:
    https://docs.djangoproject.com/en/3.0/ref/models/fields/#django.db.models.DateField.auto_now and
    https://docs.djangoproject.com/en/3.0/ref/models/fields/#django.db.models.DateField.auto_now_add for more
    information.
    """

    created_at = models.DateTimeField(_("created at"), auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(_("modified_at"), auto_now=True, editable=False)

    class Meta:
        abstract = True


class SubscriptionAbstractModel(models.Model):
    """
    Adds a ``subscription`` field to a model to map the object to a subscription.
    """

    subscription = models.ForeignKey(
        "subscription.Subscription",
        verbose_name=_("subscription"),
        related_name="%(app_label)s_%(class)s_subscription",
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True


class TimestampedModifiedByAbstractModel(ModifiedByAbstractModel, TimestampedAbstractModel):
    """
    An abstract model that inherits from :py:class:`ModifiedByAbstractModel` and :py:class:`TimestampedAbstractModel`
    Provides no further functionality.
    """

    class Meta:
        abstract = True


class CommonInfoAbstractModel(ModifiedByAbstractModel, TimestampedAbstractModel, SubscriptionAbstractModel):
    """
    An abstract model that inherits from :py:class:`ModifiedByAbstractModel`, :py:class:`TimestampedAbstractModel`
    and :py:class:`SubscriptionAbstractModel`
    Provides no further functionality.
    """

    class Meta:
        abstract = True


class UpcomingActivityAbstract(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    label = models.ForeignKey("system_preferences.Label", on_delete=models.CASCADE, blank=True, null=True)
    assign_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        abstract = True
