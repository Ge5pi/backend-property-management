from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt import views as jwt_views  # type: ignore[import]

schema_view = get_schema_view(
    openapi.Info(
        title="Property Management API",
        default_version="v1",
        description="",
        contact=openapi.Contact(
            name="",
            url="",
            email="",
        ),
        license=openapi.License(name="BSD License"),
    ),
    # public=False,
    permission_classes=[permissions.IsAdminUser],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # App URLS
    path("api/authentication/", include("authentication.urls")),
    path("api/accounting/", include("accounting.urls")),
    path("api/property/", include("property.urls")),
    path("api/dashboard/", include("dashboard.urls")),
    path("api/lease/", include("lease.urls")),
    path("api/maintenance/", include("maintenance.urls")),
    path("api/people/", include("people.urls")),
    path("api/core/", include("core.urls", namespace="core")),
    path("api/communication/", include("communication.urls")),
    path("api/system-preferences/", include("system_preferences.urls")),
    path("api/tenant/", include("tenant.urls")),
    # JWT URLS
    path("api/token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", jwt_views.TokenVerifyView.as_view(), name="token_verify"),
    # Swagger
    path(
        "",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]

if settings.DEBUG is not False:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
