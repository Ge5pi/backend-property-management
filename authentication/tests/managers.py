import pytest

from ..models import User


@pytest.mark.django_db
def test_user_manager_create_user(user_factory):
    """
    Testing :py:meth:`authentication.managers.UserManager.create_user`.
    """
    simple_user = user_factory()

    assert simple_user.is_staff is False
    assert simple_user.is_superuser is False

    with pytest.raises(Exception):
        user_factory(email=None)


@pytest.mark.django_db
def test_user_manager_create_superuser(super_user_factory):
    """
    Testing :py:meth:`authentication.managers.UserManager.create_superuser`.
    """
    super_user = super_user_factory()

    assert super_user.is_staff is True
    assert super_user.is_superuser is True

    with pytest.raises(ValueError):
        super_user_factory(is_superuser=False)

    with pytest.raises(ValueError):
        super_user_factory(is_staff=False)


@pytest.mark.django_db
def test_user_manager_slug_queryset(user_factory):
    """
    Testing :py:meth:`authentication.managers.UserQueryset.annotate_slug`.
    """

    user = user_factory()

    users = User.objects.annotate_slug()  # type: ignore[attr-defined]

    assert users.count() == 1
    assert users.get().slug == f"{User.SLUG}-{user.id}"


@pytest.mark.django_db
def test_user_annotate_is_tenant_is_admin(user_factory, lease_factory, subscription_factory):
    """
    Testing :py:meth:`authentication.managers.UserQueryset.annotate_is_tenant_is_admin`.
    """

    user = user_factory()
    subscription = subscription_factory(purchased_by=user)
    user.associated_subscription = subscription
    user.save()
    lease_1 = lease_factory(subscription=subscription, status="ACTIVE")
    lease_2 = lease_factory(subscription=subscription)

    staff_user = user_factory()

    users = User.objects.annotate_is_tenant_is_admin()

    assert users.count() == 4

    assert users.get(id=user.id).is_admin is True
    assert users.get(id=user.id).is_subscription_staff is True
    assert users.get(id=user.id).is_tenant is False
    assert users.get(id=lease_1.primary_tenant.user.id).is_admin is False
    assert users.get(id=lease_1.primary_tenant.user.id).is_tenant is True
    assert users.get(id=lease_1.primary_tenant.user.id).is_subscription_staff is False
    assert users.get(id=lease_2.primary_tenant.user.id).is_admin is False
    assert users.get(id=lease_2.primary_tenant.user.id).is_tenant is False
    assert users.get(id=lease_2.primary_tenant.user.id).is_subscription_staff is False
    assert users.get(id=staff_user.id).is_admin is False
    assert users.get(id=staff_user.id).is_tenant is False
    assert users.get(id=staff_user.id).is_subscription_staff is True
