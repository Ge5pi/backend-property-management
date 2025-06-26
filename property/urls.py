from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    PortfolioPropertiesListAPIView,
    PropertyAttachmentViewSet,
    PropertyLateFeePolicyViewSet,
    PropertyLeaseRenewalAttachmentViewSet,
    PropertyLeaseTemplateAttachmentViewSet,
    PropertyOwnerViewSet,
    PropertyPhotoViewSet,
    PropertyUpcomingActivityViewSet,
    PropertyUtilityBillingViewSet,
    PropertyViewSet,
    RentableItemViewSet,
    UnitPhotoViewSet,
    UnitTypePhotoViewSet,
    UnitTypeViewSet,
    UnitUpcomingActivityViewSet,
    UnitViewSet,
)

app_name = "property"

router = DefaultRouter()

router.register("properties", PropertyViewSet, basename="property")
router.register("upcoming-activities", PropertyUpcomingActivityViewSet, basename="property_upcoming_activity")
router.register("unit-upcoming-activities", UnitUpcomingActivityViewSet, basename="unit_upcoming_activity")
router.register("utility-billings", PropertyUtilityBillingViewSet, basename="property_utility_billing")
router.register("late-fee-policies", PropertyLateFeePolicyViewSet, basename="property_late_fee_policy")
router.register("attachments", PropertyAttachmentViewSet, basename="property_attachments")
router.register("photos", PropertyPhotoViewSet, basename="property_photos")
router.register("owners", PropertyOwnerViewSet, basename="property_owners")
router.register(
    "lease-template-attachments",
    PropertyLeaseTemplateAttachmentViewSet,
    basename="property_lease_template_attachments",
)
router.register(
    "lease-renewal-attachments", PropertyLeaseRenewalAttachmentViewSet, basename="property_lease_renewal_attachments"
)
router.register("units", UnitViewSet, basename="unit")
router.register("unit-types", UnitTypeViewSet, basename="unit_type")
router.register("rentable-items", RentableItemViewSet, basename="rentable_items")
router.register("unit-photos", UnitPhotoViewSet, basename="unit_photos")
router.register("unit-type-photos", UnitTypePhotoViewSet, basename="unit_type_photos")


urlpatterns = [
    path("", include(router.urls)),
    path("portfolio-properties/", PortfolioPropertiesListAPIView.as_view(), name="portfolio_properties"),
]
