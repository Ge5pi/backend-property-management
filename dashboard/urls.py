from rest_framework.routers import DefaultRouter

from .views import DashboardStatsDataViewSet, GeneralStatsDataViewSet

app_name = "dashboard"

router = DefaultRouter()
router.register("dashboard-stats", DashboardStatsDataViewSet, basename="dashboard-stats")
router.register("general-stats", GeneralStatsDataViewSet, basename="general-stats")

urlpatterns = router.urls
