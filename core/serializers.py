from typing import List, Optional

from rest_framework import serializers

from authentication.serializers.user import UserSerializer
from lease.models import RentalApplicationTemplate


class UploadSignedURLSerializer(serializers.Serializer):
    file_name = serializers.CharField()


class ModifiedByAbstractSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    modified_by = UserSerializer(read_only=True)

    class Meta:
        fields = ["created_by", "modified_by"]

    def save(self, **kwargs):
        if not self.instance:
            self.validated_data["created_by"] = self.context["request"].user
            self.validated_data["subscription"] = self.context["request"].user.associated_subscription
        self.validated_data["modified_by"] = self.context["request"].user
        return super().save(**kwargs)


class ModelChoicesSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(required=False)
    selected_steps = serializers.SerializerMethodField()
    tenant_id = serializers.IntegerField(required=False)
    tenant_first_name = serializers.CharField(required=False)
    tenant_last_name = serializers.CharField(required=False)
    is_late_fee_policy_configured = serializers.BooleanField(required=False)
    is_occupied = serializers.BooleanField(required=False)

    class Meta:
        model = None

    def get_selected_steps(self, obj) -> Optional[List[str]]:
        if isinstance(obj, RentalApplicationTemplate):
            fields = [
                "general_info",
                "personal_details",
                "rental_history",
                "financial_info",
                "dependents_info",
                "other_info",
            ]
            return [field for field in fields if getattr(obj, field)]
        else:
            return None
