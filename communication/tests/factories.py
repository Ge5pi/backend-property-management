import factory  # type: ignore[import]
from faker import Faker

from core.tests import BaseAttachmentFactory, SubscriptionAbstractFactory


class ContactFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "communication.Contact"

    name = factory.Faker("name")
    email = factory.Faker("email")
    website = factory.Faker("url")
    category = factory.SubFactory("system_preferences.tests.factories.ContactCategoryFactory")
    primary_contact = factory.LazyFunction(lambda: "+1" + Faker().msisdn())
    secondary_contact = factory.LazyFunction(lambda: "+1" + Faker().msisdn())
    street_address = factory.Faker("street_address")
    display_to_tenants = factory.Faker("boolean")
    selective = factory.Faker("boolean")


class NoteFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "communication.Note"

    title = factory.Faker("name")
    description = factory.Faker("text")
    associated_property = factory.SubFactory("property.tests.factories.PropertyFactory")

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        for tag in extracted:
            self.tags.add(tag)


class NoteAttachmentFactory(BaseAttachmentFactory):
    class Meta:
        model = "communication.NoteAttachment"
        abstract = False

    note = factory.SubFactory("communication.tests.factories.NoteFactory")


class EmailSignatureFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "communication.EmailSignature"

    text = factory.Faker("text")
    image = factory.Faker("file_path")


class BaseEmailAbstractFactory(SubscriptionAbstractFactory):
    class Meta:
        abstract = True

    subject = factory.Faker("name")
    body = factory.Faker("text")
    recipient_type = "INDIVIDUAL"
    individual_recipient_type = "VENDOR"
    signature = factory.SubFactory("communication.tests.factories.EmailSignatureFactory")
    created_by = factory.SubFactory("authentication.tests.factories.UserFactory")

    @factory.post_generation
    def vendors(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        for vendor in extracted:
            self.vendors.add(vendor)


class EmailTemplateFactory(BaseEmailAbstractFactory):
    class Meta:
        model = "communication.EmailTemplate"
        abstract = False


class EmailFactory(BaseEmailAbstractFactory):
    class Meta:
        model = "communication.Email"
        abstract = False

    template = factory.SubFactory("communication.tests.factories.EmailTemplateFactory")
    recipient_emails = factory.List([factory.Faker("email")])


class EmailAttachmentFactory(BaseAttachmentFactory):
    class Meta:
        model = "communication.EmailAttachment"
        abstract = False

    email = factory.SubFactory("communication.tests.factories.EmailFactory")


class AnnouncementFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "communication.Announcement"

    title = factory.Faker("word")
    body = factory.Faker("text")
    send_by_email = False
    display_on_tenant_portal = factory.Faker("boolean")
    display_date = factory.Faker("date_object")
    expiry_date = factory.Faker("date_object")

    @factory.post_generation
    def properties(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        for prop in extracted:
            self.properties.add(prop)

    @factory.post_generation
    def units(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        for unit in extracted:
            self.units.add(unit)


class AnnouncementAttachmentFactory(BaseAttachmentFactory):
    class Meta:
        model = "communication.AnnouncementAttachment"
        abstract = False

    announcement = factory.SubFactory("communication.tests.factories.AnnouncementFactory")
