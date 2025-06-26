import pytest


@pytest.mark.django_db
def test_update_role_user_groups(user_factory, group_factory, role_factory):
    """
    Testing :py:func:`authentication.models.update_role_user_groups` signal
    """
    group = group_factory()
    user = user_factory()
    role = role_factory(groups=(group,), users=(user,))

    assert user.groups.get() == group

    role.groups.clear()

    assert user.groups.count() == 0

    role.groups.add(group)

    assert user.groups.get() == group

    role.users.clear()

    assert user.groups.count() == 0
