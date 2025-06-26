from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, mixins, viewsets

from core.mixins import FilterQuerysetByAssociatedSubscriptionMixin
from property.models import Unit
from property.serializers import UnitListSerializer

from .filters import AnnouncementFilter
from .models import (
    Announcement,
    AnnouncementAttachment,
    Contact,
    Email,
    EmailSignature,
    EmailTemplate,
    Note,
    NoteAttachment,
)
from .serializers import (
    AnnouncementAttachmentSerializer,
    AnnouncementSerializer,
    ContactSerializer,
    EmailSerializer,
    EmailSignatureSerializer,
    EmailTemplateSerializer,
    NoteAttachmentSerializer,
    NoteSerializer,
)


class ContactViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = Contact.objects.all().order_by("-pk")
    serializer_class = ContactSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "email", "primary_contact"]


class NoteViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = (
        Note.objects.all()
        .select_related("created_by", "modified_by", "associated_property")
        .prefetch_related("tags")
        .order_by("-pk")
    )
    serializer_class = NoteSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["pk", "title", "associated_property"]


class NoteAttachmentViewSet(
    FilterQuerysetByAssociatedSubscriptionMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = NoteAttachmentSerializer
    queryset = NoteAttachment.objects.all().order_by("-pk")


class NoteAttachmentByNoteListAPIView(FilterQuerysetByAssociatedSubscriptionMixin, generics.ListAPIView):
    queryset = NoteAttachment.objects.all()
    serializer_class = NoteAttachmentSerializer

    def get_queryset(self):
        return super().get_queryset().filter(note=self.kwargs.get("note_id")).order_by("-pk")


class EmailSignatureViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = EmailSignature.objects.all().order_by("-pk")
    serializer_class = EmailSignatureSerializer


class MyEmailSignatureViewSet(
    FilterQuerysetByAssociatedSubscriptionMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    queryset = EmailSignature.objects.all()
    serializer_class = EmailSignatureSerializer

    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user).order_by("-pk")


class EmailTemplateViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = (
        EmailTemplate.objects.all()
        .select_related("created_by", "signature")
        .prefetch_related("tenants", "owners", "vendors", "units")
        .order_by("-pk")
    )
    serializer_class = EmailTemplateSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "subject",
        "body",
        "tenants__email",
        "owners__personal_emails",
        "owners__company_emails",
        "vendors__personal_emails",
        "vendors__business_emails",
    ]
    ordering_fields = ["pk", "subject", "body"]


class EmailViewSet(
    FilterQuerysetByAssociatedSubscriptionMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        Email.objects.all()
        .select_related("created_by", "signature")
        .prefetch_related("tenants", "owners", "vendors", "units")
        .order_by("-pk")
    )
    serializer_class = EmailSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ["subject", "body", "recipient_emails"]
    ordering_fields = ["pk", "subject", "body", "created_at"]
    filterset_fields = ["vendors"]


class AnnouncementViewSet(FilterQuerysetByAssociatedSubscriptionMixin, viewsets.ModelViewSet):
    queryset = Announcement.objects.all().prefetch_related("units", "properties").order_by("-pk")
    serializer_class = AnnouncementSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ["title", "body"]
    ordering_fields = ["pk", "title", "created_at"]
    filterset_class = AnnouncementFilter


class AnnouncementAttachmentViewSet(
    FilterQuerysetByAssociatedSubscriptionMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AnnouncementAttachmentSerializer
    queryset = AnnouncementAttachment.objects.all().order_by("-pk")


class AnnouncementAttachmentByAnnouncementListAPIView(
    FilterQuerysetByAssociatedSubscriptionMixin, generics.ListAPIView
):
    queryset = AnnouncementAttachment.objects.all()
    serializer_class = AnnouncementAttachmentSerializer

    def get_queryset(self):
        return super().get_queryset().filter(announcement=self.kwargs.get("announcement_id")).order_by("-pk")


class AnnouncementUnitsListAPIView(FilterQuerysetByAssociatedSubscriptionMixin, generics.ListAPIView):
    queryset = Unit.objects.all()
    serializer_class = UnitListSerializer

    def get_queryset(self):
        units = (
            super()
            .get_queryset()
            .filter(parent_property=self.kwargs.get("property_id"), announcement=self.kwargs.get("announcement_id"))
            .order_by("-pk")
        )
        return units
