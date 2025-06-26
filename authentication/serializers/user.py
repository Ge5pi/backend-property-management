from typing import List, Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer  # type: ignore[import]

User = get_user_model()


class AdminTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        email = attrs.get("email")
        try:
            user = User.objects.annotate_is_tenant_is_admin().get(email=email)
            data["is_admin"] = user.is_admin

            if (user.is_admin or user.is_subscription_staff) and user.associated_subscription is not None:
                return data
            else:
                raise serializers.ValidationError(
                    {"detail": "You are not allowed to login. Please contact your administrator."}
                )

        except ObjectDoesNotExist:
            pass


class TenantTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        email = attrs.get("email")
        try:
            user = User.objects.annotate_is_tenant_is_admin().get(email=email)
            data["is_tenant"] = user.is_tenant

            if (not user.is_admin and user.is_tenant) and user.associated_subscription is not None:
                return data
            else:
                raise serializers.ValidationError(
                    {"detail": "You are not allowed to login. Please contact your administrator."}
                )

        except ObjectDoesNotExist:
            pass


class UserSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True)
    groups = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  # type: ignore[var-annotated]
    group_names = serializers.SerializerMethodField()
    is_admin = serializers.BooleanField(read_only=True)
    is_tenant = serializers.BooleanField(read_only=True)
    is_subscription_staff = serializers.BooleanField(read_only=True)
    purchased_subscription = serializers.PrimaryKeyRelatedField(read_only=True)  # type: ignore[var-annotated]

    class Meta:
        model = User
        fields = (
            "id",
            "slug",
            "first_name",
            "last_name",
            "username",
            "email",
            "company_name",
            "telephone_number",
            "mobile_number",
            "secondary_email",
            "other_information",
            "is_staff",
            "is_active",
            "is_superuser",
            "date_joined",
            "last_login",
            "groups",
            "roles",
            "group_names",
            "is_admin",
            "is_tenant",
            "is_subscription_staff",
            "purchased_subscription",
        )

    read_only_fields = ("id", "date_joined", "last_login", "is_superuser", "is_staff", "is_active")

    def create(self, validated_data):
        roles = validated_data.pop("roles", [])
        validated_data["associated_subscription"] = self.context["request"].user.associated_subscription
        user = User(**validated_data)
        User.objects.set_random_password(user)
        user.save()
        user.roles.add(*roles)
        return user

    def update(self, instance, validated_data):
        roles = validated_data.pop("roles", [])
        instance = super().update(instance, validated_data)
        instance.roles.clear()
        instance.roles.add(*roles)
        return instance

    def get_group_names(self, obj) -> Optional[List[str]]:
        if isinstance(obj, User):
            return list(obj.groups.values_list("name", flat=True))
        else:
            return None


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("id", "name")
