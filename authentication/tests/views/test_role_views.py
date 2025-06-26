import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from authentication.models import Role
from authentication.views import RoleViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 6),
        ({"search": "Toward"}, [1], 4),
        ({"search": "Kitchen occur side personal"}, [2], 4),
    ),
)
@pytest.mark.django_db
def test_role_list(api_rf, user_with_permissions, role_factory, query_params, index_result, num_queries):
    """
    Testing :py:meth:`authentication.views.RoleViewSet.list` method.
    """
    user = user_with_permissions([("authentication", "role")])

    instance_1 = role_factory(
        name="Fly.", description="Example game ten near current", subscription=user.associated_subscription
    )
    instance_2 = role_factory(
        name="Toward.", description="Dinner nature soon girl mind.", subscription=user.associated_subscription
    )
    instance_3 = role_factory(
        name="Himself.",
        description="Kitchen occur side personal race economic.",
        subscription=user.associated_subscription,
    )

    roles = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("authentication:role-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = RoleViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [roles[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "groups": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "name": "Group 1",
                "description": "Lorem Ipsum Dolor",
                "groups": [0],
            },
            None,
            201,
            10,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_role_create(
    api_rf, user_with_permissions, data, expected_response, status_code, num_queries, obj_count, group_factory
):
    """
    Testing :py:meth:`authentication.views.RoleViewSet.create` method.
    """
    group_1 = group_factory()
    groups = [group_1.pk]
    user = user_with_permissions([("authentication", "role")])
    if status_code == 201:
        data["groups"] = [groups[i] for i in data["groups"]]

    with assertNumQueries(num_queries):
        url = reverse("authentication:role-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = RoleViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert Role.objects.count() == obj_count


@pytest.mark.django_db
def test_role_retrieve(api_rf, role_factory, user_with_permissions):
    """
    Testing :py:meth:`authentication.views.RoleViewSet.retrieve` method.
    """

    user = user_with_permissions([("authentication", "role")])
    role = role_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse("authentication:role-detail", kwargs={"pk": role.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = RoleViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=role.id)

    assert response.status_code == 200

    assert response.data.keys() == {"id", "name", "description", "groups", "users_count"}


@pytest.mark.django_db
def test_role_update(api_rf, role_factory, group_factory, user_with_permissions):
    """
    Testing :py:meth:`authentication.views.RoleViewSet.partial_update` method.
    """

    user = user_with_permissions([("authentication", "role")])
    group = group_factory()
    role = role_factory(subscription=user.associated_subscription)
    data = {
        "name": "Group 1",
        "description": "Lorem Ipsum Dolor",
        "groups": [group.pk],
    }

    with assertNumQueries(11):
        url = reverse("authentication:role-detail", kwargs={"pk": role.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = RoleViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=role.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_role_delete(api_rf, role_factory, user_with_permissions):
    """
    Testing :py:meth:`authentication.views.RoleViewSet.delete` method.
    """

    user = user_with_permissions([("authentication", "role")])
    role = role_factory(subscription=user.associated_subscription)

    with assertNumQueries(6):
        url = reverse("authentication:role-detail", kwargs={"pk": role.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = RoleViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=role.id)

    assert response.status_code == 204

    assert Role.objects.count() == 0
