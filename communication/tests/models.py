from datetime import datetime

import pytest

from core.models import BaseAttachment

from ..models import (
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


@pytest.mark.django_db
def test_contact(contact_factory, contact_category_factory):
    """
    Testing :py:class:`communication.models.Contact` model with factory
    """
    contact_category = contact_category_factory()
    contact = contact_factory(
        name="James Ramirez",
        email="johnson@example.net",
        website="http://www.webb-macdonald.com/",
        category=contact_category,
        primary_contact="+1-522-103-2058",
        secondary_contact="+1-522-103-2059",
        street_address="7267 Martin Loop Apt. 459",
        display_to_tenants=True,
        selective=False,
    )

    contacts = Contact.objects.all()
    assert contacts.count() == 1
    assert contact.name == "James Ramirez"
    assert contact.email == "johnson@example.net"
    assert contact.website == "http://www.webb-macdonald.com/"
    assert contact.category == contact_category
    assert contact.primary_contact == "+1-522-103-2058"
    assert contact.secondary_contact == "+1-522-103-2059"
    assert contact.street_address == "7267 Martin Loop Apt. 459"
    assert contact.display_to_tenants == True  # noqa
    assert contact.selective == False  # noqa
    assert str(contact) == "James Ramirez"


@pytest.mark.django_db
def test_note(note_factory, property_factory, tag_factory):
    """
    Testing :py:class:`communication.models.Note` model with factory
    """
    associated_property = property_factory()
    tag = tag_factory()
    note = note_factory(
        title="James Ramirez",
        description="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        associated_property=associated_property,
        tags=(tag,),
    )

    notes = Note.objects.all()
    assert notes.count() == 1
    assert note.title == "James Ramirez"
    assert note.description == "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    assert note.associated_property == associated_property
    assert note.tags.get() == tag
    assert str(note) == "James Ramirez"


@pytest.mark.django_db
def test_note_attachment(note_attachment_factory, note_factory):
    """
    Testing :py:class:`communication.models.NoteAttachment` model with factory
    """
    note = note_factory()
    note_attachment = note_attachment_factory(name="Property Agreement", file="test.pdf", file_type="pdf", note=note)

    note_attachments = NoteAttachment.objects.all()
    assert note_attachments.count() == 1
    assert note_attachment.name == "Property Agreement"
    assert note_attachment.file == "test.pdf"
    assert note_attachment.file_type == "pdf"
    assert note_attachment.note == note
    assert str(note_attachment) == "Property Agreement"
    assert isinstance(note_attachment, BaseAttachment)


@pytest.mark.django_db
def test_email_signature(email_signature_factory):
    """
    Testing :py:class:`communication.models.EmailSignature` model with factory
    """
    email_signature = email_signature_factory(
        text="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        image="test.jpg",
    )

    email_signatures = EmailSignature.objects.all()
    assert email_signatures.count() == 1
    assert email_signature.text == "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    assert email_signature.image == "test.jpg"
    assert str(email_signature) == "Lorem ipsum dolor sit amet, consectetur adipiscing elit."


@pytest.mark.django_db
def test_email_template(email_template_factory, email_signature_factory, vendor_factory):
    """
    Testing :py:class:`communication.models.EmailTemplate` model with factory
    """
    email_signature = email_signature_factory()
    vendor = vendor_factory()
    email_template = email_template_factory(
        subject="James Ramirez",
        body="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        recipient_type="INDIVIDUAL",
        individual_recipient_type="VENDOR",
        signature=email_signature,
        vendors=(vendor,),
    )

    email_templates = EmailTemplate.objects.all()
    assert email_templates.count() == 1
    assert email_template.subject == "James Ramirez"
    assert email_template.body == "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    assert email_template.recipient_type == "INDIVIDUAL"
    assert email_template.individual_recipient_type == "VENDOR"
    assert email_template.signature == email_signature
    assert email_template.vendors.get() == vendor
    assert str(email_template) == "James Ramirez"


@pytest.mark.django_db
def test_email(email_factory, email_template_factory, email_signature_factory, vendor_factory):
    """
    Testing :py:class:`communication.models.Email` model with factory
    """
    email_signature = email_signature_factory()
    vendor = vendor_factory()
    email_template = email_template_factory()
    email = email_factory(
        subject="James Ramirez",
        body="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        recipient_type="INDIVIDUAL",
        individual_recipient_type="VENDOR",
        signature=email_signature,
        template=email_template,
        vendors=(vendor,),
    )

    emails = Email.objects.all()
    assert emails.count() == 1
    assert email.subject == "James Ramirez"
    assert email.body == "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    assert email.recipient_type == "INDIVIDUAL"
    assert email.individual_recipient_type == "VENDOR"
    assert email.signature == email_signature
    assert email.template == email_template
    assert email.vendors.get() == vendor
    assert str(email) == "James Ramirez"


@pytest.mark.django_db
def test_email_attachment(email_attachment_factory, email_factory):
    """
    Testing :py:class:`communication.models.EmailAttachment` model with factory
    """
    email = email_factory()
    email_attachment = email_attachment_factory(
        name="Property Agreement", file="test.pdf", file_type="pdf", email=email
    )

    email_attachments = EmailAttachment.objects.all()
    assert email_attachments.count() == 1
    assert email_attachment.name == "Property Agreement"
    assert email_attachment.file == "test.pdf"
    assert email_attachment.file_type == "pdf"
    assert email_attachment.email == email
    assert str(email_attachment) == "Property Agreement"
    assert isinstance(email_attachment, BaseAttachment)


@pytest.mark.django_db
def test_announcement(announcement_factory, property_factory, unit_type_factory, unit_factory):
    """
    Testing :py:class:`communication.models.Announcement` model with factory
    """
    prop = property_factory()
    unit_type = unit_type_factory(parent_property=prop)
    unit = unit_factory(unit_type=unit_type)
    announcement = announcement_factory(
        title="James Ramirez",
        body="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        send_by_email=True,
        display_on_tenant_portal=False,
        display_date=datetime(2023, 1, 1),
        expiry_date=datetime(2023, 2, 1),
        properties=(prop,),
        units=(unit,),
    )

    announcements = Announcement.objects.all()
    assert announcements.count() == 1
    assert announcement.title == "James Ramirez"
    assert announcement.body == "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    assert announcement.send_by_email
    assert not announcement.display_on_tenant_portal
    assert announcement.display_date == datetime(2023, 1, 1)
    assert announcement.expiry_date == datetime(2023, 2, 1)
    assert announcement.properties.get() == prop
    assert announcement.units.get() == unit
    assert str(announcement) == "James Ramirez"


@pytest.mark.django_db
def test_announcement_attachment(announcement_attachment_factory, announcement_factory):
    """
    Testing :py:class:`communication.models.AnnouncementAttachment` model with factory
    """
    announcement = announcement_factory()
    announcement_attachment = announcement_attachment_factory(
        name="Property Agreement",
        file="test.pdf",
        file_type="pdf",
        announcement=announcement,
    )

    announcement_attachments = AnnouncementAttachment.objects.all()
    assert announcement_attachments.count() == 1
    assert announcement_attachment.name == "Property Agreement"
    assert announcement_attachment.file == "test.pdf"
    assert announcement_attachment.file_type == "pdf"
    assert announcement_attachment.announcement == announcement
    assert str(announcement_attachment) == "Property Agreement"
    assert isinstance(announcement_attachment, BaseAttachment)
