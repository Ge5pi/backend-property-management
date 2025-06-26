from django.contrib.auth.models import Group
from rest_framework import serializers

from authentication.models import Role
from core.serializers import ModifiedByAbstractSerializer


class RoleSerializer(ModifiedByAbstractSerializer):
    users_count = serializers.IntegerField(read_only=True)
    groups = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), required=True, many=True)

    class Meta:
        model = Role
        fields = ("id", "name", "description", "groups", "users_count")
        read_only_fields = ("id", "users_count")
