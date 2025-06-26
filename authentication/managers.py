import random
import string

from django.conf import settings
from django.contrib.auth.models import UserManager as DefaultUserManager
from django.core.mail import send_mail
from django.db.models import BooleanField, Case, Exists, F, OuterRef, Q, Subquery, Value, When
from django.db.models.query import QuerySet

from core.managers import SlugQuerysetMixin


class UserQueryset(QuerySet, SlugQuerysetMixin):
    def annotate_is_tenant_is_admin(self):
        from people.models import Tenant

        active_tenants_subquery = Tenant.objects.filter(user=OuterRef("pk"), lease__status="ACTIVE")
        tenants_subquery = Tenant.objects.filter(user=OuterRef("pk"))
        return self.annotate(
            is_admin=Case(
                When(
                    Q(purchased_subscription__isnull=False) & Q(associated_subscription=F("purchased_subscription")),
                    then=Value(True),
                ),
                default=Value(False),
                output_field=BooleanField(),
            ),
            is_tenant=Case(
                When(
                    Exists(Subquery(active_tenants_subquery)),
                    then=Value(True),
                ),
                default=Value(False),
                output_field=BooleanField(),
            ),
            is_subscription_staff=Case(
                When(
                    ~Exists(Subquery(tenants_subquery)),
                    then=Value(True),
                ),
                default=Value(False),
                output_field=BooleanField(),
            ),
        )


class BaseUserManager(DefaultUserManager):
    """
    Custom user manager to make email field required.
    """

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Users require an email field")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def set_random_password(self, user):
        password = "".join(
            [random.choice(string.ascii_letters + string.digits + string.punctuation) for n in range(12)]
        )
        user.set_password(password)
        user.save()

        send_mail(
            "Welcome to Property Management System",
            f"You have been added to the Property Management System. Your email is: {user.email} and password is: {password}. Please login to the system and change your password.\nLogin at http://ppm.meganoslab.com/tenant",  # noqa
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )

        return password


class UserManager(BaseUserManager.from_queryset(UserQueryset)):  # type: ignore[misc]
    pass
