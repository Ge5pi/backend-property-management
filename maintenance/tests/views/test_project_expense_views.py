import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from maintenance.models import ProjectExpense
from maintenance.views import ProjectExpenseViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"search": "cost go major"}, [0], 3),
        ({"search": "inside interesting else"}, [2], 3),
        ({"ordering": "title"}, [0, 1, 2], 3),
        ({"ordering": "-title"}, [2, 1, 0], 3),
        ({"ordering": "created_at"}, [0, 1, 2], 3),
        ({"ordering": "-created_at"}, [2, 1, 0], 3),
        ({"ordering": "amount"}, [0, 1, 2], 3),
        ({"ordering": "-amount"}, [2, 1, 0], 3),
        ({"project": 0}, [2], 4),
    ),
)
@pytest.mark.django_db
def test_project_expense_list(
    api_rf,
    user_with_permissions,
    project_factory,
    project_expense_factory,
    query_params,
    index_result,
    num_queries,
    freezer,
):
    """
    Testing :py:meth:`maintenance.views.ProjectExpenseViewSet.list` method.
    """
    user = user_with_permissions([("maintenance", "projectexpense")])
    project = project_factory()

    if "project" in query_params:
        query_params["project"] = project.id

    freezer.move_to("2023-01-01 00:00:00")
    instance_1 = project_expense_factory(
        title="Actually cost go major",
        description="Sing democratic decade",
        amount="12.00",
        subscription=user.associated_subscription,
    )
    freezer.move_to("2023-01-03 00:00:00")
    instance_2 = project_expense_factory(
        title="Author simple bed",
        description="popular right crime hotel",
        amount="34.00",
        subscription=user.associated_subscription,
    )
    freezer.move_to("2023-01-05 00:00:00")
    instance_3 = project_expense_factory(
        title="Food inside interesting else know task",
        description="What lot yeah benefit",
        amount="50.00",
        project=project,
        subscription=user.associated_subscription,
    )
    project_expense_factory()

    project_expenses = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("maintenance:project_expense-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = ProjectExpenseViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [project_expenses[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "project": ["This field is required."],
                "title": ["This field is required."],
                "amount": ["This field is required."],
                "date": ["This field is required."],
                "assigned_to": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "title": "Fan",
                "amount": "10.00",
                "date": "2020-01-01",
            },
            None,
            201,
            5,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_project_expense_create(
    api_rf, user_with_permissions, project_factory, data, expected_response, status_code, num_queries, obj_count
):
    """
    Testing :py:meth:`maintenance.views.ProjectExpenseViewSet.create` method.
    """

    user = user_with_permissions([("maintenance", "projectexpense")])

    if status_code == 201:
        project = project_factory()
        data["project"] = project.id
        data["assigned_to"] = user.id

    with assertNumQueries(num_queries):
        url = reverse("maintenance:project_expense-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = ProjectExpenseViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert ProjectExpense.objects.count() == obj_count


@pytest.mark.django_db
def test_project_expense_retrieve(api_rf, project_expense_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.ProjectExpenseViewSet.retrieve` method.
    """

    user = user_with_permissions([("maintenance", "projectexpense")])
    project_expense = project_expense_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse("maintenance:project_expense-detail", kwargs={"pk": project_expense.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = ProjectExpenseViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=project_expense.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "title",
        "amount",
        "date",
        "assigned_to",
        "project",
        "assigned_to_first_name",
        "assigned_to_last_name",
        "assigned_to_username",
    }


@pytest.mark.django_db
def test_project_expense_update(api_rf, project_expense_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.ProjectExpenseViewSet.partial_update` method.
    """

    user = user_with_permissions([("maintenance", "projectexpense")])
    project_expense = project_expense_factory(subscription=user.associated_subscription)
    data = {
        "title": "Fan",
        "amount": "10.00",
        "date": "2020-01-01",
        "assigned_to": user.id,
    }

    with assertNumQueries(5):
        url = reverse("maintenance:project_expense-detail", kwargs={"pk": project_expense.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = ProjectExpenseViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=project_expense.id)

    assert response.status_code == 200

    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_project_expense_delete(api_rf, project_expense_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.ProjectExpenseViewSet.delete` method.
    """

    user = user_with_permissions([("maintenance", "projectexpense")])
    project_expense = project_expense_factory(subscription=user.associated_subscription)

    with assertNumQueries(5):
        url = reverse("maintenance:project_expense-detail", kwargs={"pk": project_expense.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = ProjectExpenseViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=project_expense.id)

    assert response.status_code == 204

    assert ProjectExpense.objects.count() == 0
