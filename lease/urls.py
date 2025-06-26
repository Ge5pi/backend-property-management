from rest_framework.routers import DefaultRouter

from .views import (
    ApplicantViewSet,
    LeaseTemplateViewSet,
    LeaseViewSet,
    RentalApplicationAdditionalIncomeViewSet,
    RentalApplicationAttachmentViewSet,
    RentalApplicationDependentViewSet,
    RentalApplicationEmergencyContactViewSet,
    RentalApplicationFinancialInformationViewSet,
    RentalApplicationPetsViewSet,
    RentalApplicationResidentialHistoryViewSet,
    RentalApplicationTemplateViewSet,
    RentalApplicationViewSet,
    SecondaryTenantViewSet,
)

app_name = "lease"

router = DefaultRouter()
router.register(
    "rental-application-template", RentalApplicationTemplateViewSet, basename="rental-application-template"
)
router.register("lease-template", LeaseTemplateViewSet, basename="lease-template")
router.register("applicant", ApplicantViewSet, basename="applicant")
router.register("rental-application", RentalApplicationViewSet, basename="rental-application")
router.register("lease", LeaseViewSet, basename="lease")

router.register("rental-application-pet", RentalApplicationPetsViewSet, basename="rental-application-pet")
router.register(
    "rental-application-dependent", RentalApplicationDependentViewSet, basename="rental-application-dependent"
)
router.register(
    "rental-application-additional-income",
    RentalApplicationAdditionalIncomeViewSet,
    basename="rental-application-additional-income",
)
router.register(
    "rental-application-resident-history",
    RentalApplicationResidentialHistoryViewSet,
    basename="rental-application-resident-history",
)
router.register(
    "rental-application-financial-information",
    RentalApplicationFinancialInformationViewSet,
    basename="rental-application-financial-information",
)
router.register(
    "rental-application-attachment", RentalApplicationAttachmentViewSet, basename="rental-application-attachment"
)
router.register(
    "rental-application-emergency-contact",
    RentalApplicationEmergencyContactViewSet,
    basename="rental-application-emergency-contact",
)
router.register("secondary-tenant", SecondaryTenantViewSet, basename="secondary-tenant")

urlpatterns = router.urls
