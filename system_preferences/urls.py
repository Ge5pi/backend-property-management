from rest_framework.routers import DefaultRouter

from .views import (
    BusinessInformationViewSet,
    ContactCategoryViewSet,
    InventoryItemTypeViewSet,
    InventoryLocationViewSet,
    LabelViewSet,
    ManagementFeeViewSet,
    PropertyTypeViewSet,
    TagViewSet,
)

app_name = "system_preferences"

router = DefaultRouter()
router.register("property-type", PropertyTypeViewSet, basename="property-type")
router.register("inventory-item-type", InventoryItemTypeViewSet, basename="inventory-item-type")
router.register("tag", TagViewSet, basename="tag")
router.register("label", LabelViewSet, basename="label")
router.register("inventory-location", InventoryLocationViewSet, basename="inventory-location")
router.register("management-fee", ManagementFeeViewSet, basename="management-fee")
router.register("business-information", BusinessInformationViewSet, basename="business-information")
router.register("contact-category", ContactCategoryViewSet, basename="contact-category")

urlpatterns = router.urls
