# TODO: Exclude in pyproject.toml is also not working, it must be revisited
# And also we should also revisit if we can tweak around it why it is giving us the import type error
# even though we don't have direct import from `rest_framework_simplejwt.token_blacklist.models`
# or may be upgrade to the dependencies fix it automatically
# mypy: ignore-errors
import stripe
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from djstripe.models import Customer
from phonenumber_field.modelfields import PhoneNumberField

from core.models import CommonInfoAbstractModel

from .managers import UserManager


class User(AbstractUser):
    SLUG = "usr"

    email = models.EmailField(_("email address"), unique=True)

    company_name = models.CharField(max_length=100, blank=True, null=True)
    telephone_number = PhoneNumberField(blank=True, null=True)
    mobile_number = PhoneNumberField()
    secondary_email = models.EmailField(blank=True, null=True)
    other_information = models.TextField(blank=True, null=True)

    associated_subscription = models.ForeignKey(
        "subscription.Subscription",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="users",
    )

    stripe_customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="users",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "mobile_number"]

    objects = UserManager()  # type: ignore[misc]

    def __str__(self):
        return self.username


class Role(CommonInfoAbstractModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    groups = models.ManyToManyField("auth.Group", related_name="roles", blank=True)
    users = models.ManyToManyField("authentication.User", related_name="roles", blank=True)

    def __str__(self):
        return self.name


@receiver(m2m_changed, sender=Role.groups.through)
@receiver(m2m_changed, sender=Role.users.through)
def update_role_user_groups(sender, instance, action, **kwargs):
    if isinstance(instance, Role):
        if action == "pre_add" or action == "pre_remove" or action == "pre_clear":
            for user in instance.users.all():
                user.groups.clear()

        elif action == "post_add" or action == "post_remove" or action == "post_clear":
            for user in instance.users.all():
                user.groups.set(instance.groups.all())

    elif isinstance(instance, User):
        if action == "pre_add" or action == "pre_remove" or action == "pre_clear":
            instance.groups.clear()

        elif action == "post_add" or action == "post_remove" or action == "post_clear":
            instance.groups.set(instance.roles.all().values_list("groups", flat=True))


@receiver(post_save, sender=User)
def create_stripe_customer(sender, instance, created, **kwargs):
    if created and settings.ENABLE_STRIPE_CUSTOMER_CREATE:
        stripe_customer = stripe.Customer.create(email=instance.email)
        customer = Customer.sync_from_stripe_data(stripe_customer)
        instance.stripe_customer = customer
        instance.save()
