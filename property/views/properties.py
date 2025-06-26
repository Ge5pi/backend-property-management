from django.db.models import Count, F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.mixins import FilterQuerysetByAssociatedSubscriptionMixin
from property.filters import PropertyFilter, PropertyUpcomingActivityFilter
from property.models import (
    Property,
    PropertyAttachment,
    PropertyLateFeePolicy,
    PropertyLeaseRenewalAttachment,
    PropertyLeaseTemplateAttachment,
    PropertyOwner,
    PropertyPhoto,
    PropertyUpcomingActivity,
    PropertyUtilityBilling,
)
from property.serializers import (
    PortfolioPropertySerializer,
    PropertyAttachmentSerializer,
    PropertyLateFeePolicySerializer,
    PropertyLeaseRenewalAttachmentSerializer,
    PropertyLeaseTemplateAttachmentSerializer,
    PropertyListSerializer,
    PropertyOwnerSerializer,
    PropertyPhotoSerializer,
    PropertySerializer,
    PropertyUpcomingActivitySerializer,
    PropertyUtilityBillingSerializer,
    RentIncreaseSerializer,
)
from property.tasks import scheduled_rent_increase


class PropertyViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = (
        Property.objects.select_related("property_type")
        .annotate_slug()  # type: ignore[attr-defined]
        .annotate_data()  # type: ignore[attr-defined]
        .order_by("-pk")
    )
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ["pk", "name", "number_of_units", "owners__owner__first_name"]
    search_fields = ["name", "address", "slug", "property_type__name"]
    filterset_class = PropertyFilter

    def get_serializer_class(self):
        if self.action == "list" or self.action == "vacant_properties":
            return PropertyListSerializer
        elif self.action == "rent_increase":
            return RentIncreaseSerializer
        else:
            return PropertySerializer

    @action(
        detail=True,
        methods=["post"],
        url_path="rent-increase",
    )
    def rent_increase(self, request, *args, **kwargs):
        """
        Rent increase for a property
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        units = instance.units.all()
        if serializer.validated_data["schedule_increase"]:
            scheduled_rent_increase.apply_async(
                (
                    instance.id,
                    serializer.validated_data["rent_increase"],
                    serializer.validated_data["rent_increase_type"],
                ),
                eta=serializer.validated_data["schedule_increase_date"],
            )
        else:
            if serializer.validated_data["rent_increase_type"] == "percentage":
                rent_increase = F("rent") + (F("rent") * serializer.validated_data["rent_increase"] / 100)
                units.update(
                    rent=rent_increase,
                )
            elif serializer.validated_data["rent_increase_type"] == "fixed":
                rent_increase = F("rent") + serializer.validated_data["rent_increase"]
                units.update(
                    rent=rent_increase,
                )

        return Response(status=status.HTTP_200_OK)


class PropertyUpcomingActivityViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = PropertyUpcomingActivity.objects.select_related("label", "assign_to", "parent_property").order_by("-pk")
    serializer_class = PropertyUpcomingActivitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PropertyUpcomingActivityFilter


class PropertyUtilityBillingViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = PropertyUtilityBilling.objects.all().order_by("-pk")
    serializer_class = PropertyUtilityBillingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["parent_property"]


class PropertyLateFeePolicyViewSet(
    FilterQuerysetByAssociatedSubscriptionMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = PropertyLateFeePolicy.objects.all().order_by("-pk")
    serializer_class = PropertyLateFeePolicySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["parent_property"]


class PropertyAttachmentViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = PropertyAttachment.objects.all().order_by("-pk")
    serializer_class = PropertyAttachmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["parent_property"]


class PropertyPhotoViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = PropertyPhoto.objects.all().order_by("-pk")
    serializer_class = PropertyPhotoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["parent_property"]


class PropertyOwnerViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = PropertyOwner.objects.all().select_related("owner").order_by("-pk")
    serializer_class = PropertyOwnerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["parent_property"]


class PropertyLeaseTemplateAttachmentViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = PropertyLeaseTemplateAttachment.objects.all().order_by("-pk")
    serializer_class = PropertyLeaseTemplateAttachmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["parent_property"]


class PropertyLeaseRenewalAttachmentViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = PropertyLeaseRenewalAttachment.objects.all().order_by("-pk")
    serializer_class = PropertyLeaseRenewalAttachmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["parent_property"]


class PortfolioPropertiesListAPIView(FilterQuerysetByAssociatedSubscriptionMixin, generics.ListAPIView):
    queryset = (
        Property.objects.annotate_slug()  # type: ignore[attr-defined]
        .annotate_portfolio_data()  # type: ignore[attr-defined]
        .filter(occupied_units_count__lt=Count("units"))
        .distinct()
    )
    serializer_class = PortfolioPropertySerializer
