from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch, Q
from rest_framework import permissions, viewsets
from rest_framework.response import Response

from lease.models import RentalApplication
from maintenance.models import ServiceRequest, WorkOrder
from people.models import Owner, Tenant, Vendor
from property.models import Property, Unit

from .serializers import DashboardStatsDataSerializer, GeneralStatsDataSerializer

User = get_user_model()


class DashboardStatsDataViewSet(viewsets.GenericViewSet):
    serializer_class = DashboardStatsDataSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        user = request.user
        subscription_record_query = Q(subscription=user.associated_subscription)

        # Units Section
        total_units_count = Unit.objects.filter(subscription_record_query).count()
        occupied_units_count = (
            Unit.objects.filter(subscription_record_query).annotate_data().filter(is_occupied=True).count()
        )
        vacant_units_count = (
            Unit.objects.filter(subscription_record_query).annotate_data().filter(is_occupied=False).count()
        )
        occupancy_percentage = occupied_units_count / total_units_count * 100 if total_units_count else 0

        # People Section
        vendors_count = Vendor.objects.filter(subscription_record_query).count()
        tenants_count = Tenant.objects.filter(subscription_record_query).count()
        owners_count = Owner.objects.filter(subscription_record_query).count()
        users_count = User.objects.filter(associated_subscription=user.associated_subscription).count()

        # Property Section
        properties_count = Property.objects.filter(subscription_record_query).count()
        properties = (
            Property.objects.filter(subscription_record_query)
            .prefetch_related(
                Prefetch(
                    "units",
                    queryset=Unit.objects.filter(subscription_record_query).annotate_data(),
                )
            )
            .annotate(
                occupied_units_count=Count("units", filter=Q(units__leases__status="ACTIVE")),
            )
        )
        complete_occupied_properties_count = properties.filter(occupied_units_count=Count("units")).distinct().count()
        partial_occupied_properties_count = (
            properties.filter(occupied_units_count__gt=0, occupied_units_count__lt=Count("units")).distinct().count()
        )
        vacant_properties_count = properties.filter(occupied_units_count=0).distinct().count()

        stats_data = {
            "total_units_count": total_units_count,
            "occupied_units_count": occupied_units_count,
            "vacant_units_count": vacant_units_count,
            "occupancy_percentage": occupancy_percentage,
            "vendors_count": vendors_count,
            "tenants_count": tenants_count,
            "owners_count": owners_count,
            "users_count": users_count,
            "properties_count": properties_count,
            "complete_occupied_properties_count": complete_occupied_properties_count,
            "partial_occupied_properties_count": partial_occupied_properties_count,
            "vacant_properties_count": vacant_properties_count,
        }

        serializer = self.get_serializer(stats_data)

        return Response(serializer.data)


class GeneralStatsDataViewSet(viewsets.GenericViewSet):
    serializer_class = GeneralStatsDataSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        user = request.user
        subscription_record_query = Q(subscription=user.associated_subscription)
        # Service Requests
        completed_service_request_query = Q(work_orders__status=WorkOrder.StatusChoices.COMPLETED)
        completed_service_requests_count = (
            ServiceRequest.objects.filter(subscription_record_query)
            .filter(completed_service_request_query)
            .distinct()
            .count()
        )
        pending_service_requests_count = (
            ServiceRequest.objects.filter(subscription_record_query)
            .exclude(completed_service_request_query)
            .distinct()
            .count()
        )

        # Work Orders
        unassigned_work_orders_count = (
            WorkOrder.objects.filter(subscription_record_query)
            .filter(status=WorkOrder.StatusChoices.UNASSIGNED)
            .count()
        )
        open_work_orders_count = (
            WorkOrder.objects.filter(subscription_record_query).filter(status=WorkOrder.StatusChoices.OPEN).count()
        )
        assigned_work_orders_count = (
            WorkOrder.objects.filter(subscription_record_query).filter(status=WorkOrder.StatusChoices.ASSIGNED).count()
        )
        completed_work_orders_count = (
            WorkOrder.objects.filter(subscription_record_query)
            .filter(status=WorkOrder.StatusChoices.COMPLETED)
            .count()
        )

        # Rental Applications
        approved_rental_applications_count = (
            RentalApplication.objects.filter(subscription_record_query)
            .filter(status=RentalApplication.RentalApplicationStatusChoices.APPROVED)
            .count()
        )
        pending_rental_applications_count = (
            RentalApplication.objects.filter(subscription_record_query)
            .filter(status=RentalApplication.RentalApplicationStatusChoices.PENDING)
            .count()
        )
        rejected_rental_applications_count = (
            RentalApplication.objects.filter(subscription_record_query)
            .filter(status=RentalApplication.RentalApplicationStatusChoices.REJECTED)
            .count()
        )
        on_hold_rental_applications_count = (
            RentalApplication.objects.filter(subscription_record_query)
            .filter(status=RentalApplication.RentalApplicationStatusChoices.ON_HOLD_OR_WAITING)
            .count()
        )
        draft_rental_applications_count = (
            RentalApplication.objects.filter(subscription_record_query)
            .filter(status=RentalApplication.RentalApplicationStatusChoices.DRAFT)
            .count()
        )

        general_stats_data = {
            "completed_service_requests_count": completed_service_requests_count,
            "pending_service_requests_count": pending_service_requests_count,
            "unassigned_work_orders_count": unassigned_work_orders_count,
            "open_work_orders_count": open_work_orders_count,
            "assigned_work_orders_count": assigned_work_orders_count,
            "completed_work_orders_count": completed_work_orders_count,
            "approved_rental_applications_count": approved_rental_applications_count,
            "pending_rental_applications_count": pending_rental_applications_count,
            "rejected_rental_applications_count": rejected_rental_applications_count,
            "on_hold_rental_applications_count": on_hold_rental_applications_count,
            "draft_rental_applications_count": draft_rental_applications_count,
        }

        serializer = self.get_serializer(general_stats_data)

        return Response(serializer.data)
