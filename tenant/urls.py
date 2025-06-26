from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AnnouncementViewSet,
    ChargeViewSet,
    ContactViewSet,
    InvoiceViewSet,
    LeaseViewSet,
    PaymentIntentForInvoiceCreateAPIView,
    PaymentViewSet,
    ServiceRequestViewSet,
    TenantRetrieveAPIView,
    WorkOrderViewSet,
)

app_name = "tenant"

router = DefaultRouter()

router.register("charges", ChargeViewSet, basename="charge")
router.register("invoices", InvoiceViewSet, basename="invoice")
router.register("leases", LeaseViewSet, basename="lease")
router.register("service-requests", ServiceRequestViewSet, basename="service_requests")
router.register("work-orders", WorkOrderViewSet, basename="work_orders")
router.register("announcements", AnnouncementViewSet, basename="announcement")
router.register("contacts", ContactViewSet, basename="contact")
router.register("payments", PaymentViewSet, basename="payment")

urlpatterns = router.urls

urlpatterns += [
    path(
        "payment-intents-for-invoice/",
        PaymentIntentForInvoiceCreateAPIView.as_view(),
        name="payment-intent-for-invoice",
    ),
    path(
        "tenant/",
        TenantRetrieveAPIView.as_view(),
        name="tenant-retrieve",
    ),
]

if settings.DEBUG:
    from django.views.generic import TemplateView

    urlpatterns += [
        path(
            "test-stripe/",
            TemplateView.as_view(template_name="tenant/test_stripe.html"),
            name="test-stripe",
        )
    ]
