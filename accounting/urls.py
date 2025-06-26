from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AccountAttachmentViewSet,
    AccountViewSet,
    ChargeAttachmentByChargeListAPIView,
    ChargeAttachmentViewSet,
    ChargeViewSet,
    GeneralLedgerAccountViewSet,
    GeneralLedgerTransactionViewSet,
    InvoiceViewSet,
    PaymentAttachmentViewSet,
    PaymentViewSet,
)

app_name = "accounting"

router = DefaultRouter()
router.register("invoice", InvoiceViewSet, basename="invoice")
router.register("charge", ChargeViewSet, basename="charge")
router.register("charge-attachment", ChargeAttachmentViewSet, basename="charge-attachment")
router.register("account", AccountViewSet, basename="account")
router.register("account-attachment", AccountAttachmentViewSet, basename="account-attachment")
router.register("payment", PaymentViewSet, basename="payment")
router.register("payment-attachment", PaymentAttachmentViewSet, basename="payment-attachment")
router.register("general-ledger-account", GeneralLedgerAccountViewSet, basename="general-ledger-account")
router.register("general-ledger-transaction", GeneralLedgerTransactionViewSet, basename="general-ledger-transaction")

urlpatterns = router.urls

urlpatterns += [
    path("stripe/", include("djstripe.urls", namespace="djstripe")),
    path(
        "charge/<int:charge_id>/attachments/",
        ChargeAttachmentByChargeListAPIView.as_view(),
        name="charge-attachment-list",
    ),
]
