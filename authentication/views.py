from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, viewsets
from rest_framework.filters import SearchFilter

from core.mixins import FilterQuerysetByAssociatedSubscriptionMixin

from .filters import UserFilter
from .models import Role
from .serializers import GroupSerializer, UserSerializer
from .serializers.role import RoleSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.annotate_slug().annotate_is_tenant_is_admin().order_by("-pk")  # type: ignore[attr-defined]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["first_name", "last_name", "username", "email", "slug"]
    filterset_class = UserFilter
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(associated_subscription=self.request.user.associated_subscription)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all().order_by("-pk")  # type: ignore[attr-defined]
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticated,)


class CurrentUserDetailsAPIView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return User.objects.annotate_slug().annotate_is_tenant_is_admin().get(pk=self.request.user.pk)


class RoleViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = Role.objects.annotate(users_count=Count("users")).order_by("-pk")  # type: ignore[attr-defined]
    serializer_class = RoleSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name", "description"]
