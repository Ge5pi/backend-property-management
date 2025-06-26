from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Role, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "is_staff", "is_active", "is_superuser")
    list_filter = (
        "is_staff",
        "is_active",
        "is_superuser",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "username",
                    "email",
                    "password",
                )
            },
        ),
        (
            _("Subscription"),
            {"fields": ("associated_subscription",)},
        ),
        (
            _("Stripe"),
            {"fields": ("stripe_customer",)},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    ordering = ("username",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "description")
    filter_horizontal = ("groups", "users")
