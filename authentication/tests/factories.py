import factory  # type: ignore[import]
from django.conf import settings
from faker import Faker

from core.tests import SubscriptionAbstractFactory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.Sequence(lambda n: "user_%d" % n)
    email = factory.Sequence(lambda n: "user_%d@example.com" % n)
    password = factory.Faker("password", length=12, digits=True)
    company_name = factory.Faker("company")
    telephone_number = factory.LazyFunction(lambda: "+1" + Faker().msisdn())
    mobile_number = factory.LazyFunction(lambda: "+1" + Faker().msisdn())
    secondary_email = factory.Faker("email")
    other_information = factory.Faker("text")
    is_active = True
    associated_subscription = factory.SubFactory("subscription.tests.SubscriptionFactory")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Use ``create_user`` instead of the manager's default ``create`` function to create an object."""
        manager = cls._get_manager(model_class)
        # create_user takes email and password as positional arguments
        username = kwargs.pop("username")
        email = kwargs.pop("email")
        password = kwargs.pop("password")
        user = manager.create_user(username=username, email=email, password=password, **kwargs)
        user.set_password(password)
        return user


class SuperUserFactory(UserFactory):
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Use ``create_user`` instead of the manager's default ``create`` function to create an object."""
        manager = cls._get_manager(model_class)
        # create_user takes email and password as positional arguments
        username = kwargs.pop("username")
        email = kwargs.pop("email")
        password = kwargs.pop("password")
        user = manager.create_superuser(username=username, email=email, password=password, **kwargs)
        return user


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "auth.Group"

    name = factory.Sequence(lambda n: "group_%d" % n)


class RoleFactory(SubscriptionAbstractFactory):
    class Meta:
        model = "authentication.Role"

    name = factory.Sequence(lambda n: "role_%d" % n)
    description = factory.Faker("text")

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        for group in extracted:
            self.groups.add(group)

    @factory.post_generation
    def users(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        for user in extracted:
            self.users.add(user)
