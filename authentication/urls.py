from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView  # type: ignore[import-untyped]

from .serializers.user import AdminTokenObtainPairSerializer, TenantTokenObtainPairSerializer
from .views import CurrentUserDetailsAPIView, GroupViewSet, RoleViewSet, UserViewSet

app_name = "authentication"

router = DefaultRouter()

router.register("users", UserViewSet, basename="user")
router.register("groups", GroupViewSet, basename="group")
router.register("roles", RoleViewSet, basename="role")

urlpatterns = router.urls
urlpatterns += [
    path("current-user-details/", CurrentUserDetailsAPIView.as_view(), name="current-user-details"),
    path(
        "admin-token/",
        TokenObtainPairView.as_view(serializer_class=AdminTokenObtainPairSerializer),
        name="admin_token_obtain_pair",
    ),
    path(
        "tenant-token/",
        TokenObtainPairView.as_view(serializer_class=TenantTokenObtainPairSerializer),
        name="tenant_token_obtain_pair",
    ),
]
