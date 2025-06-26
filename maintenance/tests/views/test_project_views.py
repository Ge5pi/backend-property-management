from datetime import date

import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from maintenance.models import Project
from maintenance.views import ProjectViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 4),
        ({"search": "cost go major"}, [0], 4),
        ({"search": "inside interesting else"}, [2], 4),
        ({"ordering": "name"}, [0, 1, 2], 4),
        ({"ordering": "-name"}, [2, 1, 0], 4),
        ({"ordering": "start_date"}, [0, 1, 2], 4),
        ({"ordering": "-start_date"}, [2, 1, 0], 4),
        ({"ordering": "end_date"}, [0, 1, 2], 4),
        ({"ordering": "-end_date"}, [2, 1, 0], 4),
        ({"ordering": "status"}, [2, 1, 0], 4),
        ({"ordering": "-status"}, [0, 1, 2], 4),
        ({"ordering": "budget"}, [0, 1, 2], 4),
        ({"ordering": "-budget"}, [2, 1, 0], 4),
        ({"ordering": "parent_property__name"}, [0, 1, 2], 4),
        ({"ordering": "-parent_property__name"}, [2, 1, 0], 4),
        ({"parent_property": 0}, [0], 5),
        ({"status": "IN_PROGRESS"}, [1], 4),
    ),
)
@pytest.mark.django_db
def test_project_list(
    api_rf, user_with_permissions, property_factory, project_factory, query_params, index_result, num_queries
):
    """
    Testing :py:meth:`maintenance.views.ProjectViewSet.list` method.
    """
    user = user_with_permissions([("maintenance", "project")])
    parent_property_1 = property_factory(name="Property 1")
    parent_property_2 = property_factory(name="Property 2")
    parent_property_3 = property_factory(name="Property 3")

    if "parent_property" in query_params:
        query_params["parent_property"] = parent_property_1.id

    instance_1 = project_factory(
        name="Actually cost go major",
        description="Sing democratic decade",
        status="PENDING",
        start_date=date(2023, 1, 1),
        end_date=date(2023, 1, 1),
        budget="100.00",
        parent_property=parent_property_1,
        subscription=user.associated_subscription,
    )
    instance_2 = project_factory(
        name="Author simple bed",
        description="popular right crime hotel",
        status="IN_PROGRESS",
        start_date=date(2023, 1, 2),
        end_date=date(2023, 1, 2),
        budget="200.00",
        parent_property=parent_property_2,
        subscription=user.associated_subscription,
    )
    instance_3 = project_factory(
        name="Food inside interesting else know task",
        description="What lot yeah benefit",
        status="COMPLETED",
        start_date=date(2023, 1, 4),
        end_date=date(2023, 1, 4),
        budget="300.00",
        parent_property=parent_property_3,
        subscription=user.associated_subscription,
    )
    project_factory()

    projects = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("maintenance:project-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = ProjectViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [projects[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "description": ["This field is required."],
                "parent_property": ["This field is required."],
                "select_all_units": ["This field is required."],
                "budget": ["This field is required."],
                "gl_account": ["This field is required."],
                "start_date": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "name": "Fan",
                "description": "Read line shake short term.",
                "status": "PENDING",
                "budget": "10.00",
                "gl_account": "12345",
                "start_date": "2020-01-01",
                "end_date": "2020-01-01",
                "select_all_units": True,
            },
            None,
            201,
            9,
            1,
        ),
        (
            {
                "name": "Fan",
                "description": "Read line shake short term.",
                "status": "PENDING",
                "budget": "10.00",
                "gl_account": "12345",
                "start_date": "2020-01-01",
                "end_date": "2020-01-01",
                "select_all_units": False,
            },
            None,
            201,
            9,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_project_create(
    api_rf,
    user_with_permissions,
    property_factory,
    unit_type_factory,
    unit_factory,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`maintenance.views.ProjectViewSet.create` method.
    """

    user = user_with_permissions([("maintenance", "project")])
    prop = property_factory()
    unit_type = unit_type_factory(parent_property=prop)
    unit_factory(unit_type=unit_type)
    unit_factory(unit_type=unit_type)

    if status_code == 201:
        data["parent_property"] = prop.id
        if not data.get("select_all_units"):
            unit = unit_factory()
            data["units"] = [unit.id]

    with assertNumQueries(num_queries):
        url = reverse("maintenance:project-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = ProjectViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert Project.objects.count() == obj_count

    if status_code == 201:
        project = Project.objects.first()
        if data.get("select_all_units"):
            assert project.units.count() == 2
        else:
            assert project.units.count() == 1
            assert project.units.first() == unit


@pytest.mark.django_db
def test_project_retrieve(api_rf, project_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.ProjectViewSet.retrieve` method.
    """

    user = user_with_permissions([("maintenance", "project")])
    project = project_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse("maintenance:project-detail", kwargs={"pk": project.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = ProjectViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=project.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "name",
        "description",
        "status",
        "get_status_display",
        "parent_property",
        "units",
        "select_all_units",
        "budget",
        "gl_account",
        "start_date",
        "end_date",
        "parent_property_name",
    }


@pytest.mark.django_db
def test_project_update(api_rf, project_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.ProjectViewSet.partial_update` method.
    """

    user = user_with_permissions([("maintenance", "project")])
    project = project_factory(subscription=user.associated_subscription)
    data = {
        "name": "Fan",
        "description": "Read line shake short term.",
        "status": "PENDING",
        "parent_property": project.parent_property.id,
        "budget": "10.00",
        "gl_account": "12345",
        "start_date": "2020-01-01",
        "end_date": "2020-01-01",
    }

    with assertNumQueries(7):
        url = reverse("maintenance:project-detail", kwargs={"pk": project.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = ProjectViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=project.id)

    assert response.status_code == 200

    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_project_delete(api_rf, project_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.ProjectViewSet.delete` method.
    """

    user = user_with_permissions([("maintenance", "project")])
    project = project_factory(subscription=user.associated_subscription)

    with assertNumQueries(7):
        url = reverse("maintenance:project-detail", kwargs={"pk": project.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = ProjectViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=project.id)

    assert response.status_code == 204

    assert Project.objects.count() == 0
