import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from maintenance.models import ProjectExpenseAttachment
from maintenance.views import ProjectExpenseAttachmentViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"project_expense": 1}, [1, 0], 4),
    ),
)
@pytest.mark.django_db
def test_project_expense_attachment_list(
    api_rf,
    query_params,
    index_result,
    num_queries,
    user_with_permissions,
    project_expense_attachment_factory,
    project_expense_factory,
):
    """
    Testing :py:meth:`maintenance.views.ProjectExpenseAttachmentListAPIView` method.
    """
    user = user_with_permissions([("maintenance", "projectexpenseattachment")])
    project_expense = project_expense_factory(subscription=user.associated_subscription)

    if "project_expense" in query_params:
        query_params["project_expense"] = project_expense.id

    instance_1 = project_expense_attachment_factory(
        project_expense=project_expense, subscription=user.associated_subscription
    )
    instance_2 = project_expense_attachment_factory(
        project_expense=project_expense, subscription=user.associated_subscription
    )
    instance_3 = project_expense_attachment_factory(subscription=user.associated_subscription)
    project_expense_attachment_factory()

    project_expense_attachments = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("maintenance:project_expense_attachments-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = ProjectExpenseAttachmentViewSet.as_view({"get": "list"})
        response = view(request, project_expense_id=project_expense.id)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [project_expense_attachments[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "project_expense": ["This field is required."],
                "file": ["This field is required."],
                "name": ["This field is required."],
                "file_type": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            None,
            201,
            8,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_project_expense_attachment_create(
    api_rf,
    project_expense_factory,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`maintenance.views.ProjectExpenseAttachmentViewSet.create` method.
    """

    user = user_with_permissions([("maintenance", "projectexpenseattachment")])
    project_expense = project_expense_factory(
        subscription=user.associated_subscription,
    )

    if status_code == 201:
        data["project_expense"] = project_expense.id

    with assertNumQueries(num_queries):
        url = reverse("maintenance:project_expense_attachments-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = ProjectExpenseAttachmentViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert ProjectExpenseAttachment.objects.count() == obj_count


@pytest.mark.django_db
def test_project_expense_attachment_retrieve(
    api_rf, project_expense_attachment_factory, project_expense_factory, user_with_permissions
):
    """
    Testing :py:meth:`maintenance.views.ProjectExpenseAttachmentViewSet.retrieve` method.
    """

    user = user_with_permissions([("maintenance", "projectexpenseattachment")])
    project_expense_attachment = project_expense_attachment_factory(
        subscription=user.associated_subscription,
    )

    with assertNumQueries(3):
        url = reverse(
            "maintenance:project_expense_attachments-detail",
            kwargs={"pk": project_expense_attachment.id},
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = ProjectExpenseAttachmentViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=project_expense_attachment.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "name",
        "created_by",
        "file",
        "project_expense",
        "file_type",
        "updated_at",
    }


@pytest.mark.django_db
def test_project_expense_attachment_update(
    api_rf, project_expense_attachment_factory, user_with_permissions, project_expense_factory
):
    """
    Testing :py:meth:`maintenance.views.ProjectExpenseAttachmentViewSet.partial_update` method.
    """

    user = user_with_permissions([("maintenance", "projectexpenseattachment")])
    project_expense = project_expense_factory(
        subscription=user.associated_subscription,
    )
    project_expense_attachment = project_expense_attachment_factory(
        subscription=user.associated_subscription,
    )
    data = {
        "project_expense": project_expense.id,
        "file": "Agreement.pdf",
        "name": "Agreement",
        "file_type": "pdf",
    }

    with assertNumQueries(5):
        url = reverse(
            "maintenance:project_expense_attachments-detail",
            kwargs={"pk": project_expense_attachment.id},
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = ProjectExpenseAttachmentViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=project_expense_attachment.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_project_expense_attachment_delete(api_rf, project_expense_attachment_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.ProjectExpenseAttachmentViewSet.delete` method.
    """

    user = user_with_permissions([("maintenance", "projectexpenseattachment")])
    project_expense_attachment = project_expense_attachment_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse(
            "maintenance:project_expense_attachments-detail",
            kwargs={"pk": project_expense_attachment.id},
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = ProjectExpenseAttachmentViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=project_expense_attachment.id)

    assert response.status_code == 204

    assert ProjectExpenseAttachment.objects.count() == 0
