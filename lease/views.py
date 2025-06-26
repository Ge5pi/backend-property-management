from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from core.mixins import FilterQuerysetByAssociatedSubscriptionMixin

from .filters import LeaseFilter
from .models import (
    Applicant,
    Lease,
    LeaseTemplate,
    RentalApplication,
    RentalApplicationAdditionalIncome,
    RentalApplicationAttachment,
    RentalApplicationDependent,
    RentalApplicationEmergencyContact,
    RentalApplicationFinancialInformation,
    RentalApplicationPets,
    RentalApplicationResidentialHistory,
    RentalApplicationTemplate,
    SecondaryTenant,
)
from .serializers import (
    ApplicantSerializer,
    LeaseSerializer,
    LeaseTemplateSerializer,
    RentalApplicationAdditionalIncomeSerializer,
    RentalApplicationAttachmentSerializer,
    RentalApplicationDependentSerializer,
    RentalApplicationEmergencyContactSerializer,
    RentalApplicationFinancialInformationSerializer,
    RentalApplicationPetsSerializer,
    RentalApplicationResidentialHistorySerializer,
    RentalApplicationSerializer,
    RentalApplicationTemplateSerializer,
    SecondaryTenantSerializer,
)


class RentalApplicationTemplateViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = RentalApplicationTemplate.objects.all().order_by("-pk")
    serializer_class = RentalApplicationTemplateSerializer
    search_fields = ["name", "description"]
    ordering_fields = ["name", "description", "created_at"]
    filter_backends = [SearchFilter, OrderingFilter]


class LeaseTemplateViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = LeaseTemplate.objects.all().order_by("-pk")
    serializer_class = LeaseTemplateSerializer
    ordering_fields = ["name", "description", "created_at"]
    search_fields = ["name", "description"]
    filter_backends = [SearchFilter, OrderingFilter]


class ApplicantViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = Applicant.objects.prefetch_related("unit", "unit__parent_property").order_by("-pk")
    serializer_class = ApplicantSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["unit", "unit__parent_property", "rental_application__status"]
    search_fields = ["first_name", "last_name", "email", "phone_number"]
    ordering_fields = ["first_name", "last_name", "email", "phone_number", "unit__name"]

    def perform_create(self, serializer):
        super().perform_create(serializer)
        if serializer.validated_data.get("allow_email_for_rental_application"):
            # TODO: send email for rental application
            print("Sending Mail for Rental Application")


class RentalApplicationViewSet(
    mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    queryset = RentalApplication.objects.annotate_slug().order_by("-pk")  # type: ignore[attr-defined]
    serializer_class = RentalApplicationSerializer

    def perform_destroy(self, instance):
        is_lease_created = instance.leases.exists()

        if not is_lease_created:
            super().perform_destroy(instance)
        else:
            raise ValidationError("Cannot delete rental application after lease is created")


class RentalApplicationResidentialHistoryViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    serializer_class = RentalApplicationResidentialHistorySerializer
    queryset = RentalApplicationResidentialHistory.objects.all().order_by("-pk")
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["rental_application"]


class RentalApplicationFinancialInformationViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    serializer_class = RentalApplicationFinancialInformationSerializer
    queryset = RentalApplicationFinancialInformation.objects.all().order_by("-pk")
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["rental_application"]


class RentalApplicationAdditionalIncomeViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    serializer_class = RentalApplicationAdditionalIncomeSerializer
    queryset = RentalApplicationAdditionalIncome.objects.all().order_by("-pk")
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["rental_application"]


class RentalApplicationDependentViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    serializer_class = RentalApplicationDependentSerializer
    queryset = RentalApplicationDependent.objects.all().order_by("-pk")
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["rental_application"]


class RentalApplicationPetsViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    serializer_class = RentalApplicationPetsSerializer
    queryset = RentalApplicationPets.objects.all().order_by("-pk")
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["rental_application"]


class RentalApplicationEmergencyContactViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    serializer_class = RentalApplicationEmergencyContactSerializer
    queryset = RentalApplicationEmergencyContact.objects.all().order_by("-pk")
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["rental_application"]


class RentalApplicationAttachmentViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    serializer_class = RentalApplicationAttachmentSerializer
    queryset = RentalApplicationAttachment.objects.all().order_by("-pk")
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["rental_application"]


class LeaseViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = Lease.objects.prefetch_related("primary_tenant", "rental_application", "unit").order_by("-pk")

    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = [
        "start_date",
        "end_date",
        "primary_tenant__first_name",
        "primary_tenant__last_name",
        "unit__name",
    ]
    search_fields = ["tenant__first_name", "tenant__last_name"]
    filterset_class = LeaseFilter
    serializer_class = LeaseSerializer

    def perform_destroy(self, instance):
        if instance.status == Lease.LeaseStatus.CLOSED:
            super().perform_destroy(instance)
        else:
            raise ValidationError("Lease cannot be deleted if it is not closed")

    @action(
        detail=True,
        methods=["post"],
        url_path="close",
    )
    def close(self, request, pk=None):
        lease = self.get_object()
        if lease.status == Lease.LeaseStatus.ACTIVE:
            lease.close_lease()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "Lease is already closed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=True,
        methods=["post"],
        url_path="renewal",
    )
    def renewal(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance.close_lease()
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SecondaryTenantViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = SecondaryTenant.objects.all().order_by("-pk")
    serializer_class = SecondaryTenantSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["lease"]
