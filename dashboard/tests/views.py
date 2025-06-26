import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from dashboard.views import DashboardStatsDataViewSet, GeneralStatsDataViewSet


@pytest.mark.django_db
def test_dashboard_stats_data_list(
    api_rf,
    owner_people_factory,
    vendor_factory,
    lease_factory,
    user_factory,
    subscription_factory,
    property_factory,
    unit_type_factory,
    unit_factory,
):
    """
    Testing :py:class:`dashboard.views.DashboardStatsDataViewSet.list`
    """
    subscription = subscription_factory()
    user = user_factory(associated_subscription=subscription)
    vendor_factory(subscription=subscription)
    owner_people_factory(subscription=subscription)
    prop = property_factory(subscription=subscription)
    unit_type = unit_type_factory(subscription=subscription, parent_property=prop)
    unit = unit_factory(subscription=subscription, unit_type=unit_type)
    lease_factory(subscription=subscription, unit=unit)
    stats_data = {
        "total_units_count": 1,
        "occupied_units_count": 0,
        "vacant_units_count": 1,
        "occupancy_percentage": 0.0,
        "vendors_count": 1,
        "tenants_count": 1,
        "owners_count": 1,
        "users_count": 2,
        "properties_count": 1,
        "complete_occupied_properties_count": 0,
        "partial_occupied_properties_count": 0,
        "vacant_properties_count": 1,
    }

    with assertNumQueries(11):
        url = reverse("dashboard:dashboard-stats-list")
        request = api_rf.get(url, format="json")
        request.user = user
        view = DashboardStatsDataViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert response.data == stats_data


@pytest.mark.django_db
def test_general_stats_data_list(api_rf, user_factory, service_request_factory, work_order_factory, applicant_factory):
    """
    Testing :py:class:`dashboard.views.GeneralStatsDataViewSet.list`
    """
    user = user_factory()
    service_request = service_request_factory(subscription=user.associated_subscription)
    work_order_factory(service_request=service_request, subscription=user.associated_subscription)
    applicant_factory(subscription=user.associated_subscription)

    stats_data = {
        "completed_service_requests_count": 0,
        "pending_service_requests_count": 1,
        "unassigned_work_orders_count": 0,
        "open_work_orders_count": 1,
        "assigned_work_orders_count": 0,
        "completed_work_orders_count": 0,
        "approved_rental_applications_count": 0,
        "pending_rental_applications_count": 0,
        "rejected_rental_applications_count": 0,
        "on_hold_rental_applications_count": 0,
        "draft_rental_applications_count": 1,
    }

    with assertNumQueries(11):
        url = reverse("dashboard:general-stats-list")
        request = api_rf.get(url, format="json")
        request.user = user
        view = GeneralStatsDataViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert response.data == stats_data
