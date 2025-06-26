import factory  # type: ignore[import]
from faker import Faker

from core.tests import SubscriptionAbstractFactory


class PropertyTypeFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "system_preferences.PropertyType"
        django_get_or_create = ("name",)

    name = factory.Faker("sentence", nb_words=3)


class InventoryItemTypeFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "system_preferences.InventoryItemType"
        django_get_or_create = ("name",)

    name = factory.Faker("sentence", nb_words=3)


class TagFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "system_preferences.Tag"
        django_get_or_create = ("name",)

    name = factory.Faker("sentence", nb_words=3)


class LabelFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "system_preferences.Label"
        django_get_or_create = ("name",)

    name = factory.Faker("sentence", nb_words=3)


class InventoryLocationFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "system_preferences.InventoryLocation"
        django_get_or_create = ("name",)

    name = factory.Faker("sentence", nb_words=3)


class ManagementFeeFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "system_preferences.ManagementFee"

    fee = factory.Faker("pydecimal", left_digits=4, right_digits=2, positive=True)
    fee_type = "FLAT_FEE"
    gl_account = factory.LazyAttribute(lambda a: str(factory.Faker("random_number")))


class BusinessInformationFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "system_preferences.BusinessInformation"

    logo = factory.Faker("uri")
    name = factory.Faker("name")
    description = factory.Faker("sentence", nb_words=30)
    building_or_office_number = factory.Faker("building_number")
    street = factory.Faker("street_address")
    city = factory.Faker("city")
    state = factory.Faker("country_code")
    postal_code = factory.Faker("postalcode")
    country = factory.Faker("country")
    primary_email = factory.Faker("email")
    secondary_email = factory.Faker("email")
    phone_number = factory.LazyFunction(lambda: "+1" + Faker().msisdn())
    telephone_number = factory.LazyFunction(lambda: "+1" + Faker().msisdn())
    tax_identity_type = factory.Faker("word")
    tax_payer_id = factory.Faker("word")


class ContactCategoryFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "system_preferences.ContactCategory"
        django_get_or_create = ("name",)

    name = factory.Faker("sentence", nb_words=3)
