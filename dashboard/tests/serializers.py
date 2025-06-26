import pytest

from dashboard.serializers import DashboardStatsDataSerializer, GeneralStatsDataSerializer


@pytest.mark.django_db
def test_dashboard_stats_data_serializer():
    """
    Testing :py:class:`communication.serializers.DashboardStatsDataSerializer` serializer
    """

    data = {
        "total_units_count": 1,
        "occupied_units_count": 1,
        "vacant_units_count": 1,
        "occupancy_percentage": 1.0,
        "vendors_count": 1,
        "tenants_count": 1,
        "owners_count": 1,
        "users_count": 1,
        "properties_count": 1,
        "complete_occupied_properties_count": 1,
        "partial_occupied_properties_count": 1,
        "vacant_properties_count": 1,
    }

    serializer = DashboardStatsDataSerializer(data)

    assert serializer.data == data


@pytest.mark.django_db
def test_general_stats_data_serializer():
    """
    Testing :py:class:`communication.serializers.GeneralStatsDataSerializer` serializer
    """

    data = {
        "completed_service_requests_count": 1,
        "pending_service_requests_count": 1,
        "unassigned_work_orders_count": 1,
        "open_work_orders_count": 1,
        "assigned_work_orders_count": 1,
        "completed_work_orders_count": 1,
        "approved_rental_applications_count": 1,
        "pending_rental_applications_count": 1,
        "rejected_rental_applications_count": 1,
        "on_hold_rental_applications_count": 1,
        "draft_rental_applications_count": 1,
    }

    serializer = GeneralStatsDataSerializer(data)

    assert serializer.data == data
