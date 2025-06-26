import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from accounting.models import AccountAttachment
from accounting.views import AccountAttachmentViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"account": 1}, [1, 0], 4),
    ),
)
@pytest.mark.django_db
def test_account_attachment_list(
    api_rf, query_params, index_result, num_queries, user_with_permissions, account_attachment_factory, account_factory
):
    """
    Testing :py:meth:`accounting.views.AccountAttachmentByAccountListAPIView` method.
    """
    user = user_with_permissions([("accounting", "accountattachment")])
    account = account_factory(subscription=user.associated_subscription)

    if "account" in query_params:
        query_params["account"] = account.id

    instance_1 = account_attachment_factory(account=account, subscription=user.associated_subscription)
    instance_2 = account_attachment_factory(account=account, subscription=user.associated_subscription)
    instance_3 = account_attachment_factory(subscription=user.associated_subscription)
    account_attachment_factory()

    account_attachments = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("accounting:account-attachment-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = AccountAttachmentViewSet.as_view({"get": "list"})
        response = view(request, account_id=account.id)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [account_attachments[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "account": ["This field is required."],
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
def test_account_attachment_create(
    api_rf,
    account_factory,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`accounting.views.AccountAttachmentViewSet.create` method.
    """

    user = user_with_permissions([("accounting", "accountattachment")])
    account = account_factory(
        subscription=user.associated_subscription,
    )

    if status_code == 201:
        data["account"] = account.id

    with assertNumQueries(num_queries):
        url = reverse("accounting:account-attachment-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = AccountAttachmentViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert AccountAttachment.objects.count() == obj_count


@pytest.mark.django_db
def test_account_attachment_retrieve(api_rf, account_attachment_factory, account_factory, user_with_permissions):
    """
    Testing :py:meth:`accounting.views.AccountAttachmentViewSet.retrieve` method.
    """

    user = user_with_permissions([("accounting", "accountattachment")])
    account_attachment = account_attachment_factory(
        subscription=user.associated_subscription,
    )

    with assertNumQueries(3):
        url = reverse(
            "accounting:account-attachment-detail",
            kwargs={"pk": account_attachment.id},
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = AccountAttachmentViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=account_attachment.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "name",
        "created_by",
        "file",
        "account",
        "file_type",
        "updated_at",
    }


@pytest.mark.django_db
def test_account_attachment_update(api_rf, account_attachment_factory, user_with_permissions, account_factory):
    """
    Testing :py:meth:`accounting.views.AccountAttachmentViewSet.partial_update` method.
    """

    user = user_with_permissions([("accounting", "accountattachment")])
    account = account_factory(
        subscription=user.associated_subscription,
    )
    account_attachment = account_attachment_factory(
        subscription=user.associated_subscription,
    )
    data = {
        "account": account.id,
        "file": "Agreement.pdf",
        "name": "Agreement",
        "file_type": "pdf",
    }

    with assertNumQueries(5):
        url = reverse(
            "accounting:account-attachment-detail",
            kwargs={"pk": account_attachment.id},
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = AccountAttachmentViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=account_attachment.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_account_attachment_delete(api_rf, account_attachment_factory, user_with_permissions, account_factory):
    """
    Testing :py:meth:`accounting.views.AccountAttachmentViewSet.delete` method.
    """

    user = user_with_permissions([("accounting", "accountattachment")])
    account_attachment = account_attachment_factory(
        subscription=user.associated_subscription,
    )

    with assertNumQueries(4):
        url = reverse(
            "accounting:account-attachment-detail",
            kwargs={"pk": account_attachment.id},
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = AccountAttachmentViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=account_attachment.id)

    assert response.status_code == 204

    assert AccountAttachment.objects.count() == 0
