from django.utils import timezone
from rest_framework import serializers

from authentication.serializers import UserSerializer
from core.serializers import ModifiedByAbstractSerializer
from property.models import Property, Unit

from .models import (
    Announcement,
    AnnouncementAttachment,
    Contact,
    Email,
    EmailAttachment,
    EmailSignature,
    EmailTemplate,
    Note,
    NoteAttachment,
)
from .utils import send_email_from_email_model


class ContactSerializer(ModifiedByAbstractSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Contact
        fields = (
            "id",
            "name",
            "category",
            "category_name",
            "primary_contact",
            "secondary_contact",
            "email",
            "website",
            "street_address",
            "display_to_tenants",
            "selective",
        )


class NoteAttachmentSerializer(ModifiedByAbstractSerializer):
    created_by = UserSerializer(many=False, read_only=True)

    class Meta:
        model = NoteAttachment
        fields = (
            "id",
            "name",
            "created_by",
            "file",
            "note",
            "file_type",
            "updated_at",
        )
        read_only_fields = ("id", "created_by")


class NoteSerializer(ModifiedByAbstractSerializer):
    created_by_full_name = serializers.SerializerMethodField()
    modified_by_full_name = serializers.SerializerMethodField()
    tag_names = serializers.SerializerMethodField()
    associated_property_name = serializers.CharField(source="associated_property.name", read_only=True)
    associated_property_type_name = serializers.CharField(
        source="associated_property.property_type.name", read_only=True
    )

    class Meta:
        model = Note
        fields = (
            "id",
            "title",
            "description",
            "associated_property",
            "tags",
            "created_by_full_name",
            "modified_by_full_name",
            "tag_names",
            "created_at",
            "updated_at",
            "associated_property_name",
            "associated_property_type_name",
        )
        read_only_fields = (
            "id",
            "created_by_full_name",
            "modified_by_full_name",
            "tag_names",
            "created_at",
            "updated_at",
            "associated_property_name",
            "associated_property_type_name",
        )

    def get_created_by_full_name(self, obj):
        if isinstance(obj, Note):
            if obj.created_by:
                return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        else:
            return None

    def get_modified_by_full_name(self, obj):
        if isinstance(obj, Note):
            if obj.modified_by:
                return f"{obj.modified_by.first_name} {obj.modified_by.last_name}"
        else:
            return None

    def get_tag_names(self, obj):
        if isinstance(obj, Note):
            return obj.tags.values_list("name", flat=True)
        else:
            return []


class EmailSignatureSerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = EmailSignature
        fields = ("id", "text", "image")


class EmailTemplateSerializer(ModifiedByAbstractSerializer):
    recipient_emails = serializers.SerializerMethodField()
    created_by = UserSerializer(many=False, read_only=True)

    class Meta:
        model = EmailTemplate
        fields = (
            "id",
            "recipient_type",
            "individual_recipient_type",
            "tenants",
            "owners",
            "vendors",
            "units",
            "recipient_emails",
            "subject",
            "body",
            "signature",
            "created_at",
            "created_by",
        )
        read_only_fields = ("id",)

    def get_recipient_emails(self, obj):
        if isinstance(obj, EmailTemplate):
            return EmailTemplate.objects.get_recipient_emails(obj)
        else:
            return []


class EmailAttachmentSerializer(ModifiedByAbstractSerializer):
    created_by = UserSerializer(many=False, read_only=True)

    class Meta:
        model = EmailAttachment
        fields = (
            "id",
            "name",
            "created_by",
            "file",
            "email",
            "file_type",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "email")


class EmailSerializer(ModifiedByAbstractSerializer):
    attachments = EmailAttachmentSerializer(many=True, required=False)
    created_by = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Email
        fields = (
            "id",
            "recipient_type",
            "individual_recipient_type",
            "tenants",
            "owners",
            "vendors",
            "units",
            "recipient_emails",
            "template",
            "subject",
            "body",
            "signature",
            "attachments",
            "created_by",
            "created_at",
        )
        read_only_fields = ("id",)

    def create(self, validated_data):
        attachments_data = validated_data.pop("attachments")
        user = self.context["request"].user
        email = super().create(validated_data)
        for attachment_data in attachments_data:
            EmailAttachment.objects.create(
                email=email, created_by=user, subscription=user.associated_subscription, **attachment_data
            )
        send_email_from_email_model(email)
        return email


class AnnouncementSerializer(ModifiedByAbstractSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = (
            "id",
            "title",
            "body",
            "selection",
            "send_by_email",
            "display_on_tenant_portal",
            "display_date",
            "expiry_date",
            "properties",
            "units",
            "created_at",
            "status",
        )

    def get_status(self, obj):
        if isinstance(obj, Announcement):
            if timezone.now().date() < obj.expiry_date:
                return "Active"
            else:
                return "Expired"
        else:
            return None

    def create(self, validated_data):
        instance = super().create(validated_data)
        if instance.selection == Announcement.SelectionChoices.ALL_PROPERTIES_AND_UNITS:
            properties = Property.objects.all()
            units = Unit.objects.all()
            instance.properties.add(*properties)
            instance.units.add(*units)
        elif instance.selection == Announcement.SelectionChoices.SELECTIVE_PROPERTIES_AND_ALL_UNITS:
            units = Unit.objects.filter(parent_property__in=instance.properties.all())
            instance.units.add(*units)
        elif instance.selection == Announcement.SelectionChoices.ALL_PROPERTIES_AND_SELECTIVE_UNITS:
            properties = Property.objects.all()
            instance.properties.add(*properties)
        elif instance.selection == Announcement.SelectionChoices.SELECTIVE_PROPERTIES_AND_UNITS:
            pass

        return instance


class AnnouncementAttachmentSerializer(ModifiedByAbstractSerializer):
    created_by = UserSerializer(many=False, read_only=True)

    class Meta:
        model = AnnouncementAttachment
        fields = (
            "id",
            "name",
            "created_by",
            "file",
            "announcement",
            "file_type",
            "updated_at",
        )
        read_only_fields = ("id", "created_by")
