import boto3  # type: ignore[import]
from django.conf import settings
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounting.models import Account
from authentication.models import Role, User
from communication.models import EmailTemplate
from lease.models import Applicant, LeaseTemplate, RentalApplicationTemplate
from maintenance.models import Inventory, Project, ServiceRequest, WorkOrder
from people.models import Owner, Tenant, Vendor, VendorType
from property.models import Property, Unit, UnitType
from system_preferences.models import ContactCategory, InventoryItemType, InventoryLocation, Label, PropertyType, Tag

from .filters import ModelChoicesFilterSet, ModelChoicesSearchFilter
from .serializers import ModelChoicesSerializer, UploadSignedURLSerializer
from .utils import generate_presigned_url


class UploadSignedURL(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = UploadSignedURLSerializer(data=request.data)
        if serializer.is_valid():
            file_name = serializer.validated_data["file_name"]
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )
            client_action = "put_object"
            url = generate_presigned_url(
                s3_client,
                client_action,
                {
                    "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                    "Key": file_name,
                    "ContentType": "binary/octet-stream",
                },
                3600,
            )
            return Response({"url": url})
        else:
            return Response(serializer.errors)


class GetSignedURL(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = UploadSignedURLSerializer(data=request.data)
        if serializer.is_valid():
            file_name = serializer.validated_data["file_name"]
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )
            client_action = "get_object"
            url = generate_presigned_url(
                s3_client,
                client_action,
                {
                    "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                    "Key": file_name,
                },
                3600,
            )
            return Response({"url": url})
        else:
            return Response(serializer.errors)


class ModelChoicesListAPIView(generics.ListAPIView):
    """
    Base implementation of ListAPIView for model-choices endpoints.

    The model_label query param indicates the model class for which the choices are returned. A field name should be
    provided for each model. If no ordering configurations are provided for a model, -pk is used as the default
    ordering for all models. Soft deleted models are also returned in the choices if the with_deleted param is
    provided with the value yes.
    Originally, this idea came from :py:class`django.contrib.admin.views.autocomplete.AutocompleteJsonView` to create
    a generic endpoint for listing the choices for each model. We have added our custom implementation to take care of
    permissions, different ordering for each model, and different fields as name values for each model.
    The endpoint supports the searching capability based on the search fields specified in the search_config for each
    model.
    """

    source_model = Property
    allowed_models = {
        "accounting.Account": Account,
        "authentication.Role": Role,
        "authentication.User": User,
        "people.Vendor": Vendor,
        "people.VendorType": VendorType,
        "people.Tenant": Tenant,
        "people.Owner": Owner,
        "lease.RentalApplicationTemplate": RentalApplicationTemplate,
        "lease.LeaseTemplate": LeaseTemplate,
        "lease.Applicant": Applicant,
        "system_preferences.ContactCategory": ContactCategory,
        "system_preferences.InventoryItemType": InventoryItemType,
        "system_preferences.InventoryLocation": InventoryLocation,
        "system_preferences.PropertyType": PropertyType,
        "system_preferences.Tag": Tag,
        "system_preferences.Label": Label,
        "property.Property": Property,
        "property.UnitType": UnitType,
        "property.Unit": Unit,
        "maintenance.Inventory": Inventory,
        "maintenance.ServiceRequest": ServiceRequest,
        "maintenance.WorkOrder": WorkOrder,
        "maintenance.Project": Project,
        "communication.EmailTemplate": EmailTemplate,
    }
    model_field_names = {
        Account: ("account_title", "bank_name", "account_number", "branch_name", "branch_code", "iban"),
        Role: ("name",),
        User: ("first_name", "last_name", "username"),
        Vendor: ("first_name", "last_name"),
        VendorType: ("name",),
        Tenant: ("first_name", "last_name"),
        Owner: ("first_name", "last_name"),
        RentalApplicationTemplate: ("name",),
        LeaseTemplate: ("name",),
        Applicant: ("first_name", "last_name"),
        ContactCategory: ("name",),
        InventoryItemType: ("name",),
        InventoryLocation: ("name",),
        PropertyType: ("name",),
        Tag: ("name",),
        Label: ("name",),
        Property: ("name",),
        UnitType: ("name",),
        Unit: ("name",),
        Inventory: ("name", "cost", "quantity"),
        ServiceRequest: ("description",),
        WorkOrder: ("job_description",),
        Project: ("name",),
        EmailTemplate: ("subject", "body", "recipient_type", "individual_recipient_type"),
    }
    slug_annotated_qs = (User, Vendor, VendorType, ServiceRequest, WorkOrder, Property, Unit)
    search_config = {
        Account: ("account_title", "bank_name", "account_number", "branch_name", "branch_code", "iban"),
        Role: ("name",),
        User: ("first_name", "last_name", "email"),
        Vendor: ("first_name", "last_name"),
        VendorType: ("name",),
        Tenant: ("first_name", "last_name", "email"),
        Owner: ("first_name", "last_name"),
        RentalApplicationTemplate: ("name",),
        LeaseTemplate: ("name",),
        Applicant: ("first_name", "last_name", "email"),
        ContactCategory: ("name",),
        InventoryItemType: ("name",),
        InventoryLocation: ("name",),
        PropertyType: ("name",),
        Tag: ("name",),
        Label: ("name",),
        Property: ("name",),
        UnitType: ("name",),
        Unit: ("name",),
        Inventory: ("name",),
        ServiceRequest: ("slug", "description"),
        WorkOrder: ("slug", "job_description"),
        Project: ("name",),
        EmailTemplate: ("subject",),
    }
    filterset_config = {
        Unit: ("parent_property",),
        UnitType: ("parent_property",),
        Applicant: ("unit",),
        Vendor: ("vendor_type",),
        Tenant: ("lease__unit__parent_property",),
    }
    subscription_key = {User: "associated_subscription"}
    serializer_fields = {RentalApplicationTemplate: {"selected_steps": serializers.SerializerMethodField()}}
    model_querysets = {
        User: User.objects.annotate_is_tenant_is_admin().filter(is_tenant=False),
        Property: Property.objects.annotate_data(),
        Unit: Unit.objects.annotate_data(),
        Tenant: Tenant.objects.filter(lease__status="ACTIVE"),
    }

    filter_backends = (ModelChoicesSearchFilter, ModelChoicesFilterSet)
    permission_classes = [permissions.IsAuthenticated]

    def get_search_fields(self) -> tuple:
        return self.search_config[self.source_model]

    def list(self, request, *args, **kwargs):
        """
        Returns the choices for a specified model. The model is extracted from allowed_map by using the model_label
        query param.
        """
        model_label = self.kwargs.get("model_label")
        if model_label not in self.allowed_models:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"detail": "Requesting choices for the provided model is not allowed."},
            )
        self.source_model = self.allowed_models[model_label]
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        if self.source_model in self.model_querysets:
            qs = self.model_querysets[self.source_model]
        else:
            qs = self.source_model.objects  # type: ignore[attr-defined]

        if self.source_model in self.slug_annotated_qs:
            qs = qs.annotate_slug()  # type: ignore[attr-defined]
        if self.source_model in self.subscription_key:
            qs = qs.filter(**{self.subscription_key[self.source_model]: self.request.user.associated_subscription})
        else:
            qs = qs.filter(subscription=self.request.user.associated_subscription)
        return qs.order_by("-pk")

    def get_serializer_class(self):
        ModelChoicesSerializer.Meta.model = self.source_model
        for field_name in self.model_field_names[self.source_model]:
            setattr(ModelChoicesSerializer, field_name, serializers.CharField(read_only=True))
        ModelChoicesSerializer.Meta.fields = (
            "id",
            "slug",
            "tenant_id",
            "tenant_first_name",
            "tenant_last_name",
            "selected_steps",
            "is_late_fee_policy_configured",
            "is_occupied",
        ) + self.model_field_names[self.source_model]
        return ModelChoicesSerializer
