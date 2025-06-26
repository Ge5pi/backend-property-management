import pytest

from authentication.serializers import UserSerializer

from ..models import Announcement
from ..serializers import (
    AnnouncementAttachmentSerializer,
    AnnouncementSerializer,
    ContactSerializer,
    EmailAttachmentSerializer,
    EmailSerializer,
    EmailSignatureSerializer,
    EmailTemplateSerializer,
    NoteAttachmentSerializer,
    NoteSerializer,
)


@pytest.mark.django_db
def test_contact_serializer_read(contact_factory):
    """
    Testing :py:class:`communication.serializers.ContactSerializer` read
    """
    instance = contact_factory()

    serializer = ContactSerializer(instance)

    assert serializer.data["name"] == instance.name
    assert serializer.data["email"] == instance.email
    assert serializer.data["website"] == instance.website
    assert serializer.data["category"] == instance.category.id
    assert serializer.data["category_name"] == instance.category.name
    assert serializer.data["primary_contact"] == instance.primary_contact
    assert serializer.data["secondary_contact"] == instance.secondary_contact
    assert serializer.data["street_address"] == instance.street_address
    assert serializer.data["display_to_tenants"] == instance.display_to_tenants
    assert serializer.data["selective"] == instance.selective
    assert serializer.data.keys() == {
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
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "category": ["This field is required."],
                "primary_contact": ["This field is required."],
                "display_to_tenants": ["This field is required."],
                "selective": ["This field is required."],
            },
            False,
        ),
        (
            {
                "name": "Douglas Robinson",
                "category": 100,
                "primary_contact": "+19457028805",
                "secondary_contact": "+19457028804",
                "email": "pauldean@example.net",
                "website": "http://www.delacruz.org/",
                "street_address": "844 Dana Village Suite 122",
                "display_to_tenants": True,
                "selective": True,
            },
            {
                "name": "Douglas Robinson",
                "category": 100,
                "category_name": "author",
                "primary_contact": "+19457028805",
                "secondary_contact": "+19457028804",
                "email": "pauldean@example.net",
                "website": "http://www.delacruz.org/",
                "street_address": "844 Dana Village Suite 122",
                "display_to_tenants": True,
                "selective": True,
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_contact_serializer_write(contact_category_factory, data, response, is_valid):
    """
    Testing :py:class:`communication.serializers.ContactSerializer` write
    """
    contact_category_factory(id=100, name="author")

    serializer = ContactSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_note_serializer_read(note_factory, user_factory):
    """
    Testing :py:class:`communication.serializers.NoteSerializer` read
    """
    user = user_factory()
    instance = note_factory(created_by=user, modified_by=user)

    serializer = NoteSerializer(instance)

    assert serializer.data["title"] == instance.title
    assert serializer.data["associated_property"] == instance.associated_property.id
    assert list(serializer.data["tags"]) == list(instance.tags.values_list("id", flat=True))
    assert (
        serializer.data["created_by_full_name"] == f"{instance.created_by.first_name} {instance.created_by.last_name}"
    )
    assert (
        serializer.data["modified_by_full_name"]
        == f"{instance.modified_by.first_name} {instance.modified_by.last_name}"
    )
    assert list(serializer.data["tag_names"]) == list(instance.tags.values_list("name", flat=True))
    assert serializer.data["created_at"] is not None
    assert serializer.data["updated_at"] is not None
    assert serializer.data.keys() == {
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
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "title": ["This field is required."],
                "description": ["This field is required."],
                "associated_property": ["This field is required."],
            },
            False,
        ),
        (
            {
                "title": "Note title",
                "description": "Note description",
                "associated_property": 100,
                "tags": [100, 200],
            },
            {
                "title": "Note title",
                "description": "Note description",
                "associated_property": 100,
                "tags": [100, 200],
                "created_by_full_name": None,
                "modified_by_full_name": None,
                "tag_names": [],
                "associated_property_name": "Face ahead glass resource.",
                "associated_property_type_name": "Prop Type",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_note_serializer_write(property_factory, property_type_factory, tag_factory, data, response, is_valid):
    """
    Testing :py:class:`communication.serializers.NoteSerializer` write
    """

    prop_type = property_type_factory(name="Prop Type")
    property_factory(id=100, name="Face ahead glass resource.", property_type=prop_type)
    tag_factory(id=100, name="tag1")
    tag_factory(id=200, name="tag2")

    serializer = NoteSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_note_attachment_serializer_read(note_factory, note_attachment_factory, user_factory):
    """
    Testing :py:class:`communication.serializers.NoteAttachmentSerializer` read
    """
    note = note_factory()
    user = user_factory()
    instance = note_attachment_factory(note=note, created_by=user)

    serializer = NoteAttachmentSerializer(instance)

    assert serializer.data["note"] == note.id
    assert serializer.data["created_by"] == UserSerializer(instance.created_by).data
    assert serializer.data["file"] == instance.file
    assert serializer.data["name"] == instance.name
    assert serializer.data["file_type"] == instance.file_type
    assert serializer.data["updated_at"] is not None
    assert serializer.data.keys() == {
        "id",
        "name",
        "created_by",
        "file",
        "note",
        "file_type",
        "updated_at",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "file": ["This field is required."],
                "note": ["This field is required."],
                "file_type": ["This field is required."],
            },
            False,
        ),
        (
            {
                "note": 100,
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            {
                "note": 100,
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_note_attachment_serializer_write(note_factory, data, response, is_valid):
    """
    Testing :py:class:`communication.serializers.NoteAttachmentSerializer` write
    """

    note_factory(id=100)

    serializer = NoteAttachmentSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_email_signature_serializer_read(email_signature_factory):
    """
    Testing :py:class:`communication.serializers.EmailSignatureSerializer` read
    """
    instance = email_signature_factory()

    serializer = EmailSignatureSerializer(instance)

    assert serializer.data["text"] == instance.text
    assert serializer.data["image"] == instance.image
    assert serializer.data.keys() == {"id", "text", "image"}


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "text": ["This field is required."],
            },
            False,
        ),
        (
            {
                "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "image": "test.jpg",
            },
            {
                "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "image": "test.jpg",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_email_signature_serializer_write(data, response, is_valid):
    """
    Testing :py:class:`communication.serializers.EmailSignatureSerializer` write
    """

    serializer = EmailSignatureSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_email_template_serializer_read(email_template_factory, email_signature_factory, user_factory, vendor_factory):
    """
    Testing :py:class:`communication.serializers.EmailTemplateSerializer` read
    """
    email_signature = email_signature_factory()
    vendor = vendor_factory()
    user = user_factory()
    instance = email_template_factory(signature=email_signature, vendors=(vendor,), created_by=user)

    serializer = EmailTemplateSerializer(instance)

    assert serializer.data["recipient_type"] == instance.recipient_type
    assert serializer.data["individual_recipient_type"] == instance.individual_recipient_type
    assert serializer.data["tenants"] == []
    assert serializer.data["owners"] == []
    assert serializer.data["vendors"] == [vendor.id]
    assert serializer.data["units"] == []
    assert serializer.data["subject"] == instance.subject
    assert serializer.data["body"] == instance.body
    assert serializer.data["signature"] == email_signature.id
    assert serializer.data["created_at"] is not None
    assert serializer.data["created_by"] == UserSerializer(instance.created_by).data
    assert serializer.data.keys() == {
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
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "recipient_type": ["This field is required."],
                "subject": ["This field is required."],
                "body": ["This field is required."],
            },
            False,
        ),
        (
            {
                "recipient_type": "INDIVIDUAL",
                "individual_recipient_type": "VENDOR",
                "tenants": [],
                "owners": [],
                "vendors": [100],
                "units": [],
                "subject": "James Ramirez",
                "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "signature": 100,
            },
            {
                "recipient_type": "INDIVIDUAL",
                "individual_recipient_type": "VENDOR",
                "tenants": [],
                "owners": [],
                "vendors": [100],
                "units": [],
                "subject": "James Ramirez",
                "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "signature": 100,
                "recipient_emails": [],
            },
            True,
        ),
    ),
)
@pytest.mark.django_db(transaction=True)
def test_email_template_serializer_write(email_signature_factory, vendor_factory, data, response, is_valid):
    """
    Testing :py:class:`communication.serializers.EmailTemplateSerializer` write
    """
    email_signature_factory(id=100)
    vendor_factory(id=100)

    serializer = EmailTemplateSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_email_serializer_read(
    email_factory,
    email_template_factory,
    email_signature_factory,
    vendor_factory,
    email_attachment_factory,
    user_factory,
):
    """
    Testing :py:class:`communication.serializers.EmailSerializer` read
    """
    email_signature = email_signature_factory()
    vendor = vendor_factory()
    email_template = email_template_factory()
    user = user_factory()
    instance = email_factory(signature=email_signature, template=email_template, vendors=(vendor,), created_by=user)
    email_attachment_factory(email=instance)

    serializer = EmailSerializer(instance)

    assert serializer.data["recipient_type"] == instance.recipient_type
    assert serializer.data["individual_recipient_type"] == instance.individual_recipient_type
    assert serializer.data["tenants"] == []
    assert serializer.data["owners"] == []
    assert serializer.data["vendors"] == [vendor.id]
    assert serializer.data["units"] == []
    assert serializer.data["recipient_emails"] == instance.recipient_emails
    assert serializer.data["template"] == email_template.id
    assert serializer.data["subject"] == instance.subject
    assert serializer.data["body"] == instance.body
    assert serializer.data["signature"] == email_signature.id
    assert serializer.data["attachments"] == EmailAttachmentSerializer(instance.attachments.all(), many=True).data
    assert serializer.data["created_at"] is not None
    assert serializer.data["created_by"] == UserSerializer(instance.created_by).data
    assert serializer.data.keys() == {
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
        "created_at",
        "created_by",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "recipient_type": ["This field is required."],
                "subject": ["This field is required."],
                "body": ["This field is required."],
            },
            False,
        ),
        (
            {
                "recipient_type": "INDIVIDUAL",
                "individual_recipient_type": "VENDOR",
                "tenants": [],
                "owners": [],
                "vendors": [100],
                "units": [],
                "subject": "James Ramirez",
                "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "signature": 100,
                "attachments": [
                    {
                        "name": "Agreement.pdf",
                        "file": "Agreement.pdf",
                        "file_type": "pdf",
                    }
                ],
            },
            None,
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_email_serializer_write(email_signature_factory, vendor_factory, data, response, is_valid):
    """
    Testing :py:class:`communication.serializers.EmailSerializer` write
    """
    email_signature_factory(id=100)
    vendor_factory(id=100)

    serializer = EmailSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        if response:
            assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_announcement_serializer_read(announcement_factory, property_factory, unit_type_factory, unit_factory):
    """
    Testing :py:class:`communication.serializers.AnnouncementSerializer` read
    """
    prop = property_factory()
    unit_type = unit_type_factory(parent_property=prop)
    unit = unit_factory(unit_type=unit_type)
    instance = announcement_factory(
        properties=(prop,),
        units=(unit,),
    )

    serializer = AnnouncementSerializer(instance)

    assert serializer.data["title"] == instance.title
    assert serializer.data["body"] == instance.body
    assert serializer.data["send_by_email"] == instance.send_by_email
    assert serializer.data["display_on_tenant_portal"] == instance.display_on_tenant_portal
    assert serializer.data["display_date"] == instance.display_date.strftime("%Y-%m-%d")
    assert serializer.data["expiry_date"] == instance.expiry_date.strftime("%Y-%m-%d")
    assert serializer.data["properties"] == list(instance.properties.values_list("id", flat=True))
    assert serializer.data["units"] == list(instance.units.values_list("id", flat=True))
    assert serializer.data.keys() == {
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
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "title": ["This field is required."],
                "body": ["This field is required."],
                "send_by_email": ["This field is required."],
                "display_on_tenant_portal": ["This field is required."],
                "display_date": ["This field is required."],
                "expiry_date": ["This field is required."],
            },
            False,
        ),
        (
            {
                "title": "Lorem",
                "body": "Lorem ipsum dolor",
                "selection": "SPSU",
                "send_by_email": True,
                "display_on_tenant_portal": True,
                "display_date": "2023-09-06",
                "expiry_date": "2023-09-06",
                "properties": [100],
                "units": [100],
            },
            None,
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_announcement_serializer_write(property_factory, unit_type_factory, unit_factory, data, response, is_valid):
    """
    Testing :py:class:`communication.serializers.AnnouncementSerializer` write
    """
    prop = property_factory(id=100)
    unit_type = unit_type_factory(parent_property=prop)
    unit_factory(id=100, unit_type=unit_type)

    serializer = AnnouncementSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        if response:
            assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.parametrize(
    "data, prop_count, unit_count",
    (
        (
            {
                "title": "Lorem",
                "body": "Lorem ipsum dolor",
                "selection": "SPSU",
                "send_by_email": True,
                "display_on_tenant_portal": True,
                "display_date": "2023-09-06",
                "expiry_date": "2023-09-06",
                "properties": [100],
                "units": [100],
            },
            1,
            1,
        ),
        (
            {
                "title": "Lorem",
                "body": "Lorem ipsum dolor",
                "selection": "APAU",
                "send_by_email": True,
                "display_on_tenant_portal": True,
                "display_date": "2023-09-06",
                "expiry_date": "2023-09-06",
            },
            2,
            2,
        ),
        (
            {
                "title": "Lorem",
                "body": "Lorem ipsum dolor",
                "selection": "SPAU",
                "send_by_email": True,
                "display_on_tenant_portal": True,
                "display_date": "2023-09-06",
                "expiry_date": "2023-09-06",
                "properties": [100],
            },
            1,
            1,
        ),
        (
            {
                "title": "Lorem",
                "body": "Lorem ipsum dolor",
                "selection": "APSU",
                "send_by_email": True,
                "display_on_tenant_portal": True,
                "display_date": "2023-09-06",
                "expiry_date": "2023-09-06",
                "units": [200],
            },
            2,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_announcement_serializer_create(
    mocker, property_factory, unit_type_factory, unit_factory, data, prop_count, unit_count, user_factory
):
    """
    Testing :py:meth:`communication.serializers.AnnouncementSerializer.create` create
    """
    user = user_factory()
    request = mocker.Mock(user=user)

    prop_1 = property_factory(id=100)
    prop_2 = property_factory(id=200)
    unit_type_1 = unit_type_factory(parent_property=prop_1)
    unit_type_2 = unit_type_factory(parent_property=prop_2)
    unit_factory(id=100, unit_type=unit_type_1)
    unit_factory(id=200, unit_type=unit_type_2)

    serializer = AnnouncementSerializer(data=data, context={"request": request})
    assert serializer.is_valid()

    serializer.save()
    obj_count = Announcement.objects.count()
    announcement = Announcement.objects.get()

    assert obj_count == 1

    assert announcement.properties.count() == prop_count
    assert announcement.units.count() == unit_count


@pytest.mark.django_db
def test_announcement_attachment_serializer_read(announcement_factory, announcement_attachment_factory, user_factory):
    """
    Testing :py:class:`communication.serializers.AnnouncementAttachmentSerializer` read
    """
    announcement = announcement_factory()
    user = user_factory()
    instance = announcement_attachment_factory(announcement=announcement, created_by=user)

    serializer = AnnouncementAttachmentSerializer(instance)

    assert serializer.data["announcement"] == announcement.id
    assert serializer.data["created_by"] == UserSerializer(instance.created_by).data
    assert serializer.data["file"] == instance.file
    assert serializer.data["name"] == instance.name
    assert serializer.data["file_type"] == instance.file_type
    assert serializer.data["updated_at"] is not None
    assert serializer.data.keys() == {
        "id",
        "name",
        "created_by",
        "file",
        "announcement",
        "file_type",
        "updated_at",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "file": ["This field is required."],
                "announcement": ["This field is required."],
                "file_type": ["This field is required."],
            },
            False,
        ),
        (
            {
                "announcement": 100,
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            {
                "announcement": 100,
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_announcement_attachment_serializer_write(announcement_factory, data, response, is_valid):
    """
    Testing :py:class:`communication.serializers.AnnouncementAttachmentSerializer` write
    """

    announcement_factory(id=100)

    serializer = AnnouncementAttachmentSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response
