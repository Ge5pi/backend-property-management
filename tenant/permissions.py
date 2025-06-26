from django.contrib.auth import get_user_model
from rest_framework import permissions

from lease.models import Lease

User = get_user_model()


class IsTenantAndActivePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = User.objects.annotate_is_tenant_is_admin().get(id=request.user.id)
        return (
            user.is_tenant and user.tenants.latest("created_at").lease.status == Lease.LeaseStatus.ACTIVE
        ) or user.is_superuser
