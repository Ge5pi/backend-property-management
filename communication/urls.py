from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AnnouncementAttachmentByAnnouncementListAPIView,
    AnnouncementAttachmentViewSet,
    AnnouncementUnitsListAPIView,
    AnnouncementViewSet,
    ContactViewSet,
    EmailSignatureViewSet,
    EmailTemplateViewSet,
    EmailViewSet,
    MyEmailSignatureViewSet,
    NoteAttachmentByNoteListAPIView,
    NoteAttachmentViewSet,
    NoteViewSet,
)

app_name = "communication"

router = DefaultRouter()
router.register("contact", ContactViewSet, basename="contact")
router.register("note", NoteViewSet, basename="note")
router.register("note-attachments", NoteAttachmentViewSet, basename="note-attachment")
router.register("email-signature", EmailSignatureViewSet, basename="email-signature")
router.register("my-email-signature", MyEmailSignatureViewSet, basename="my-email-signature")
router.register("email-template", EmailTemplateViewSet, basename="email-template")
router.register("email", EmailViewSet, basename="email")
router.register("announcement", AnnouncementViewSet, basename="announcement")
router.register(
    "announcement-attachments",
    AnnouncementAttachmentViewSet,
    basename="announcement-attachment",
)


urlpatterns = [
    path("", include(router.urls)),
    path(
        "note/<int:note_id>/attachments/",
        NoteAttachmentByNoteListAPIView.as_view(),
        name="note-attachment-list",
    ),
    path(
        "announcement/<int:announcement_id>/attachments/",
        AnnouncementAttachmentByAnnouncementListAPIView.as_view(),
        name="announcement-attachment-list",
    ),
    path(
        "announcement/<int:announcement_id>/<int:property_id>/",
        AnnouncementUnitsListAPIView.as_view(),
        name="announcement-units-list",
    ),
]
