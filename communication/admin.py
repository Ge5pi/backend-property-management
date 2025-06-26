from django.contrib import admin

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


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "website")
    search_fields = ("name", "email", "website", "primary_contact", "secondary_contact")
    list_filter = ("category", "display_to_tenants", "selective")


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "associated_property")
    search_fields = ("title", "description", "associated_property")
    list_filter = ("tags",)


@admin.register(NoteAttachment)
class NoteAttachmentAdmin(admin.ModelAdmin):
    list_display = ("name", "note")
    search_fields = ("name", "note")
    list_filter = ("file_type",)


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ("subject", "body", "recipient_type")
    search_fields = ("subject", "body", "recipient_type")
    list_filter = ("recipient_type",)


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ("subject", "body", "recipient_type")
    search_fields = ("subject", "body", "recipient_type")
    list_filter = ("recipient_type",)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "send_by_email",
        "display_on_tenant_portal",
        "display_date",
        "expiry_date",
    )
    search_fields = ("title", "body")


admin.site.register(EmailSignature)
admin.site.register(EmailAttachment)
admin.site.register(AnnouncementAttachment)
