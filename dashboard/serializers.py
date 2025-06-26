from rest_framework import serializers


class DashboardStatsDataSerializer(serializers.Serializer):
    total_units_count = serializers.IntegerField()
    occupied_units_count = serializers.IntegerField()
    vacant_units_count = serializers.IntegerField()
    occupancy_percentage = serializers.FloatField()
    vendors_count = serializers.IntegerField()
    tenants_count = serializers.IntegerField()
    owners_count = serializers.IntegerField()
    users_count = serializers.IntegerField()
    properties_count = serializers.IntegerField()
    complete_occupied_properties_count = serializers.IntegerField()
    partial_occupied_properties_count = serializers.IntegerField()
    vacant_properties_count = serializers.IntegerField()


class GeneralStatsDataSerializer(serializers.Serializer):
    completed_service_requests_count = serializers.IntegerField()
    pending_service_requests_count = serializers.IntegerField()
    unassigned_work_orders_count = serializers.IntegerField()
    open_work_orders_count = serializers.IntegerField()
    assigned_work_orders_count = serializers.IntegerField()
    completed_work_orders_count = serializers.IntegerField()
    approved_rental_applications_count = serializers.IntegerField()
    pending_rental_applications_count = serializers.IntegerField()
    rejected_rental_applications_count = serializers.IntegerField()
    on_hold_rental_applications_count = serializers.IntegerField()
    draft_rental_applications_count = serializers.IntegerField()
