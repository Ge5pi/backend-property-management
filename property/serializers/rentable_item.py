from rest_framework import serializers

from core.serializers import ModifiedByAbstractSerializer
from property.models import RentableItem


class RentableItemSerializer(ModifiedByAbstractSerializer):
    tenant_first_name = serializers.CharField(source="tenant.first_name", read_only=True)
    tenant_last_name = serializers.CharField(source="tenant.last_name", read_only=True)

    class Meta:
        model = RentableItem
        fields = (
            "id",
            "name",
            "description",
            "amount",
            "gl_account",
            "tenant",
            "status",
            "parent_property",
            "tenant_first_name",
            "tenant_last_name",
        )
