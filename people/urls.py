from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    OwnerOwnedPropertiesListAPIView,
    OwnerUpcomingActivityViewSet,
    OwnerViewSet,
    TenantAttachmentViewSet,
    TenantUpcomingActivitiesViewSet,
    TenantViewSet,
    VendorAddressByVendorListAPIView,
    VendorAddressViewSet,
    VendorAttachmentViewSet,
    VendorTypeViewSet,
    VendorViewSet,
)

app_name = "people"

router = DefaultRouter()
router.register("tenants", TenantViewSet, basename="tenant")
router.register("tenants-upcoming-activity", TenantUpcomingActivitiesViewSet, basename="tenant_upcoming_activity")
router.register("vendor-type", VendorTypeViewSet, basename="vendor_type")
router.register("vendor", VendorViewSet, basename="vendor")
router.register("owner-people", OwnerViewSet, basename="owner_people")
router.register("vendor-address", VendorAddressViewSet, basename="vendor_address")
router.register("owner-upcoming-activity", OwnerUpcomingActivityViewSet, basename="owner_upcoming_activity")

vendor_router = DefaultRouter()
vendor_router.register("attachments", VendorAttachmentViewSet, basename="vendor_attachment")

tenant_router = DefaultRouter()
tenant_router.register("attachments", TenantAttachmentViewSet, basename="tenant_attachment")


urlpatterns = [
    path("", include(router.urls)),
    path("vendor/<int:vendor_id>/", include(vendor_router.urls)),
    path("tenants/<int:tenant_id>/", include(tenant_router.urls)),
    path(
        "<int:vendor_id>/vendor-address/",
        VendorAddressByVendorListAPIView.as_view(),
        name="vendor-address-by-vendor",
    ),
    path(
        "<int:owner_id>/owner-owned-properties/",
        OwnerOwnedPropertiesListAPIView.as_view(),
        name="owner-owned-properties",
    ),
]
