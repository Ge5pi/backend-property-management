from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, mixins, viewsets

from core.mixins import FilterQuerysetByAssociatedSubscriptionMixin
from property.models import PropertyOwner
from property.serializers import OwnerOwnedPropertiesListSerializer

from .filters import OwnerUpcomingActivityFilter, TenantFilter, TenantUpcomingActivityFilter
from .models import (
    Owner,
    OwnerUpcomingActivity,
    Tenant,
    TenantAttachment,
    TenantUpcomingActivity,
    Vendor,
    VendorAddress,
    VendorAttachment,
    VendorType,
)
from .serializers import (
    OwnerPeopleSerializer,
    OwnerUpcomingActivitySerializer,
    TenantAttachmentSerializer,
    TenantSerializer,
    TenantUpcomingActivitySerializer,
    VendorAddressSerializer,
    VendorAttachmentSerializer,
    VendorSerializer,
    VendorTypeSerializer,
)


class TenantViewSet(
    FilterQuerysetByAssociatedSubscriptionMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = TenantSerializer
    queryset = Tenant.objects.annotate_status().select_related("lease").order_by("-pk")
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["first_name", "last_name", "email"]
    ordering_fields = ["pk", "first_name", "last_name", "phone_number", "status"]
    filterset_class = TenantFilter


class TenantUpcomingActivitiesViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    serializer_class = TenantUpcomingActivitySerializer
    queryset = TenantUpcomingActivity.objects.all().select_related("label", "assign_to", "tenant").order_by("-pk")
    filter_backends = [DjangoFilterBackend]
    filterset_class = TenantUpcomingActivityFilter


class TenantAttachmentViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = TenantAttachment.objects.all()
    serializer_class = TenantAttachmentSerializer

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(tenant_id=self.kwargs.get("tenant_id"))
            .select_related("tenant")
            .order_by("-pk")
        )


class VendorTypeViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = VendorType.objects.annotate_slug().annotate_vendor_count().order_by("-pk")  # type: ignore[attr-defined]
    serializer_class = VendorTypeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description", "slug"]
    ordering_fields = ["pk", "name", "description", "slug", "vendor_count"]
    serializer_class = VendorTypeSerializer


class VendorViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = (
        Vendor.objects.annotate_slug().select_related("vendor_type").order_by("-pk")  # type: ignore[attr-defined]
    )
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "company_name", "slug"]
    ordering_fields = ["pk", "first_name", "last_name", "company_name", "slug"]
    serializer_class = VendorSerializer


class VendorAttachmentViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = VendorAttachment.objects.all()
    serializer_class = VendorAttachmentSerializer

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(vendor_id=self.kwargs.get("vendor_id"))
            .select_related("vendor")
            .order_by("-pk")
        )


class OwnerViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = Owner.objects.all().order_by("-pk")
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "company_name"]
    ordering_fields = ["pk", "first_name", "last_name", "company_name"]
    serializer_class = OwnerPeopleSerializer


class OwnerOwnedPropertiesListAPIView(FilterQuerysetByAssociatedSubscriptionMixin, generics.ListAPIView):
    serializer_class = OwnerOwnedPropertiesListSerializer
    queryset = PropertyOwner.objects.all().select_related("owner", "parent_property").order_by("-pk")

    def get_queryset(self):
        qs = super().get_queryset()
        owner_id = self.kwargs.get("owner_id")
        return qs.filter(owner_id=owner_id).annotate(
            number_of_units=Count("parent_property__units", distinct=True),
        )


class OwnerUpcomingActivityViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    serializer_class = OwnerUpcomingActivitySerializer
    queryset = OwnerUpcomingActivity.objects.all().select_related("label", "assign_to", "owner").order_by("-pk")
    filter_backends = [DjangoFilterBackend]
    filterset_class = OwnerUpcomingActivityFilter


class VendorAddressViewSet(
    FilterQuerysetByAssociatedSubscriptionMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = VendorAddress.objects.all().select_related("vendor").order_by("-pk")
    serializer_class = VendorAddressSerializer


class VendorAddressByVendorListAPIView(FilterQuerysetByAssociatedSubscriptionMixin, generics.ListAPIView):
    queryset = VendorAddress.objects.all()
    serializer_class = VendorAddressSerializer

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(vendor_id=self.kwargs.get("vendor_id"))
            .select_related("vendor")
            .order_by("-pk")
        )
