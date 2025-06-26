import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from authentication.views import UserViewSet

User = get_user_model()


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({"search": "ard"}, [0], 7),
        ({"search": "row"}, [0], 7),
        ({"search": "tt7"}, [0], 7),
        ({"search": "USR-999"}, [0], 7),
        ({"search": "nit"}, [1], 7),
        ({"search": "rci"}, [1], 7),
        ({"search": "eher"}, [1], 7),
        ({"search": "USR-1000"}, [1], 7),
        ({"search": "chel"}, [2], 7),
        ({"search": "llow"}, [2], 7),
        ({"search": "e_ga"}, [2], 7),
        ({"search": "USR-1001"}, [2], 7),
        ({"search": "w"}, [2, 0], 11),
        ({"search": "ga"}, [2, 1], 11),
        ({"is_tenant": True}, [1], 7),
    ),
)
@pytest.mark.django_db
def test_user_list(api_rf, user_with_permissions, lease_factory, query_params, index_result, num_queries):
    """
    Testing :py:class:`authentication.views.UserViewSet` view for reading list of users.
    """

    user_1 = user_with_permissions(
        [("authentication", "user")],
        id=999,
        first_name="Howard",
        last_name="Brown",
        username="scott72",
        email="scott72@example.com",
    )
    user_2 = user_with_permissions(
        [("authentication", "user")],
        id=1000,
        first_name="Anita",
        last_name="Garcia",
        username="chloeherrera",
        email="chloeherrera@example.com",
        associated_subscription=user_1.associated_subscription,
    )
    user_3 = user_with_permissions(
        [("authentication", "user")],
        id=1001,
        first_name="Michelle",
        last_name="Galloway",
        username="michelle_galloway",
        email="michelle_galloway@example.com",
        associated_subscription=user_1.associated_subscription,
    )

    lease = lease_factory(status="ACTIVE")
    lease.primary_tenant.user = user_2
    lease.primary_tenant.save()

    users = [user_1.pk, user_2.pk, user_3.pk]

    with assertNumQueries(num_queries):
        url = reverse("authentication:user-list")
        request = api_rf.get(url, query_params)
        request.user = user_1
        view = UserViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [u["id"] for u in response.data]
    assert response_ids == [users[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "email": ["This field is required."],
                "username": ["This field is required."],
                "mobile_number": ["This field is required."],
                "roles": ["This field is required."],
            },
            400,
            2,
            1,
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
                "roles": [0],
            },
            None,
            201,
            17,
            2,
        ),
    ),
)
@pytest.mark.django_db
def test_user_create(
    api_rf,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
    role_factory,
    group_factory,
):
    """
    Testing :py:meth:`authentication.views.UserViewSet.create` method.
    """
    user = user_with_permissions([("authentication", "user")])
    group = group_factory()
    role_1 = role_factory(groups=(group,), subscription=user.associated_subscription)
    roles = [role_1.pk]
    if status_code == 201:
        data["roles"] = [roles[i] for i in data["roles"]]

    with assertNumQueries(num_queries):
        url = reverse("authentication:user-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = UserViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert User.objects.count() == obj_count


@pytest.mark.django_db
def test_user_retrieve(api_rf, user_with_permissions):
    """
    Testing :py:meth:`authentication.views.UserViewSet.retrieve` method.
    """

    user = user_with_permissions([("authentication", "user")])

    with assertNumQueries(7):
        url = reverse("authentication:user-detail", kwargs={"pk": user.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = UserViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=user.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "slug",
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
        "is_admin",
        "is_tenant",
        "is_subscription_staff",
        "purchased_subscription",
    }


@pytest.mark.django_db
def test_user_update(api_rf, user_with_permissions):
    """
    Testing :py:meth:`authentication.views.UserViewSet.partial_update` method.
    """

    user = user_with_permissions([("authentication", "user")])
    data = {
        "first_name": "Brenda",
        "last_name": "Dillon",
        "username": "brendadillon",
        "email": "user@example.com",
        "company_name": "Black Rock",
        "telephone_number": "+923111234455",
        "mobile_number": "+923111234455",
        "secondary_email": "user@example.com",
        "other_information": "Lorem ipsum dolor sit amet.",
    }

    with assertNumQueries(14):
        url = reverse("authentication:user-detail", kwargs={"pk": user.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = UserViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=user.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_user_delete(api_rf, user_with_permissions):
    """
    Testing :py:meth:`authentication.views.UserViewSet.delete` method.
    """

    user = user_with_permissions([("authentication", "user")])

    with assertNumQueries(178):
        url = reverse("authentication:user-detail", kwargs={"pk": user.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = UserViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=user.id)

    assert response.status_code == 204

    assert User.objects.count() == 0
