import pytest

from core.models import CommonInfoAbstractModel

from ..models import Role, User


@pytest.mark.django_db
def test_user(user_factory):
    """
    Testing :py:class:`authentication.models.User` model with simple user.
    """

    user_factory(
        first_name="Brenda",
        last_name="Dillon",
        username="brendadillon",
        email="user@example.com",
        company_name="Black Rock",
        telephone_number="+92311123445",
        mobile_number="+92311123445",
        secondary_email="brenda@example.com",
        other_information="Some other information",
        is_active=True,
    )
    users = User.objects.all()

    assert users.count() == 1

    user = users.get()

    assert user.pk is not None
    assert user.first_name == "Brenda"
    assert user.last_name == "Dillon"
    assert user.username == "brendadillon"
    assert user.email == "user@example.com"
    assert user.company_name == "Black Rock"
    assert user.telephone_number == "+92311123445"
    assert user.mobile_number == "+92311123445"
    assert user.secondary_email == "brenda@example.com"
    assert user.other_information == "Some other information"
    assert str(user) == "brendadillon"
    assert user.is_active is True


@pytest.mark.django_db
def test_superuser(super_user_factory):
    """
    Testing :py:class:`authentication.models.User` model with superuser.
    """
    super_user_factory(is_active=False)
    user = User.objects.get()

    assert user.is_active is False
    assert user.is_staff is True
    assert user.is_superuser is True


@pytest.mark.django_db
def test_role(role_factory, group_factory, user_factory):
    """
    Testing :py:class:`authentication.models.GroupInfo` model.
    """
    group = group_factory()
    user = user_factory()
    role_factory(name="Accountant", description="Manage Accounts", groups=(group,), users=(user,))
    role = Role.objects.get()

    assert role.pk is not None
    assert role.name == "Accountant"
    assert role.description == "Manage Accounts"
    assert role.groups.get() == group
    assert role.users.get() == user
    assert str(role) == role.name
    assert issubclass(Role, CommonInfoAbstractModel)
