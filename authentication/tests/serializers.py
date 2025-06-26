import pytest

from authentication.serializers.role import RoleSerializer

from ..serializers import GroupSerializer, UserSerializer


@pytest.mark.django_db
def test_user_serializer_read(mocker, user_factory):
    """
    Testing :py:class:`authentication.serializers.UserSerializer` serializer for reading data.
    """
    request = mocker.MagicMock()
    user = user_factory()

    serializer = UserSerializer(user, context={"request": request})

    assert serializer.data["id"] == user.id
    assert serializer.data["username"] == user.username
    assert serializer.data["email"] == user.email
    assert serializer.data["first_name"] == user.first_name
    assert serializer.data["last_name"] == user.last_name
    assert serializer.data["company_name"] == user.company_name
    assert serializer.data["telephone_number"] == user.telephone_number
    assert serializer.data["mobile_number"] == user.mobile_number
    assert serializer.data["secondary_email"] == user.secondary_email
    assert serializer.data["other_information"] == user.other_information
    assert serializer.data["is_staff"] == user.is_staff
    assert serializer.data["is_active"] == user.is_active
    assert serializer.data["is_superuser"] == user.is_superuser
    assert serializer.data["date_joined"] == user.date_joined.isoformat().replace("+00:00", "Z")
    assert serializer.data["last_login"] == user.last_login
    assert serializer.data["groups"] == []
    assert serializer.data["roles"] == []
    assert serializer.data["group_names"] == []

    assert serializer.data.keys() == {
        "id",
        "first_name",
        "last_name",
        "username",
        "email",
        "company_name",
        "telephone_number",
        "mobile_number",
        "secondary_email",
        "other_information",
        "is_staff",
        "is_active",
        "is_superuser",
        "date_joined",
        "last_login",
        "groups",
        "roles",
        "group_names",
        "purchased_subscription",
    }


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "email": ["This field is required."],
                "username": ["This field is required."],
                "mobile_number": ["This field is required."],
                "roles": ["This field is required."],
            },
            False,
        ),
        (
            {
                "first_name": "Brenda",
                "last_name": "Dillon",
                "username": "brendadillon",
                "email": "user@example.com",
                "company_name": "Black Rock",
                "telephone_number": "+923111234455",
                "mobile_number": "+923111234455",
                "secondary_email": "user@example.com",
                "other_information": "Lorem ipsum dolor sit amet.",
            },
            {
                "first_name": "Brenda",
                "last_name": "Dillon",
                "username": "brendadillon",
                "email": "user@example.com",
                "company_name": "Black Rock",
                "telephone_number": "+923111234455",
                "mobile_number": "+923111234455",
                "secondary_email": "user@example.com",
                "other_information": "Lorem ipsum dolor sit amet.",
                "last_login": None,
                "group_names": None,
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_user_serializer_write(mocker, data, response, is_valid, role_factory):
    """
    Testing :py:class:`authentication.serializers.UserSerializer` serializer for writing data.
    """
    role = role_factory()
    request = mocker.MagicMock()

    if is_valid:
        data["roles"] = [role.id]
        response["roles"] = [role.id]

    serializer = UserSerializer(data=data, context={"request": request})

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response


@pytest.mark.django_db
def test_group_serializer_read(group_factory):
    """
    Testing :py:class:`authentication.serializers.GroupSerializer` serializer for reading data.
    """
    group = group_factory()
    serializer = GroupSerializer(group)

    assert serializer.data["id"] == group.id
    assert serializer.data["name"] == group.name

    assert serializer.data.keys() == {"id", "name"}


@pytest.mark.django_db
def test_role_serializer_read(role_factory, group_factory, user_factory):
    """
    Testing :py:class:`authentication.serializers.RoleSerializer` serializer for reading data.
    """
    group = group_factory()
    user = user_factory()
    role = role_factory(groups=(group,), users=(user,))

    serializer = RoleSerializer(role)

    assert serializer.data["id"] == role.id
    assert serializer.data["name"] == role.name
    assert serializer.data["groups"] == [group.id]

    assert serializer.data.keys() == {"id", "name", "description", "groups"}


@pytest.mark.parametrize(
    "data, response, is_valid",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "groups": ["This field is required."],
            },
            False,
        ),
        (
            {
                "name": "Group 1",
                "description": "Lorem Ipsum Dolor",
            },
            {
                "name": "Group 1",
                "description": "Lorem Ipsum Dolor",
            },
            True,
        ),
    ),
)
@pytest.mark.django_db
def test_role_serializer_write(data, response, is_valid, group_factory, user_factory):
    """
    Testing :py:class:`authentication.serializers.RoleSerializer` serializer for writing data.
    """
    user_factory()
    group = group_factory()

    if is_valid:
        data["groups"] = [group.id]
        response["groups"] = [group.id]

    serializer = RoleSerializer(data=data)

    assert serializer.is_valid() == is_valid

    if is_valid:
        assert serializer.data == response
    else:
        assert serializer.errors == response
