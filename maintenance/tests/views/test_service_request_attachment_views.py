import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from maintenance.models import ServiceRequestAttachment
from maintenance.views import ServiceRequestAttachmentViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"service_request": 1}, [1, 0], 4),
    ),
)
@pytest.mark.django_db
def test_service_request_attachment_list(
    api_rf,
    query_params,
    index_result,
    num_queries,
    user_with_permissions,
    service_request_attachment_factory,
    service_request_factory,
):
    """
    Testing :py:meth:`maintenance.views.ServiceRequestAttachmentListAPIView` method.
    """
    user = user_with_permissions([("maintenance", "servicerequestattachment")])
    service_request = service_request_factory(subscription=user.associated_subscription)

    if "service_request" in query_params:
        query_params["service_request"] = service_request.id

    instance_1 = service_request_attachment_factory(
        service_request=service_request, subscription=user.associated_subscription
    )
    instance_2 = service_request_attachment_factory(
        service_request=service_request, subscription=user.associated_subscription
    )
    instance_3 = service_request_attachment_factory(subscription=user.associated_subscription)
    service_request_attachment_factory()

    service_request_attachments = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("maintenance:service_request_attachments-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = ServiceRequestAttachmentViewSet.as_view({"get": "list"})
        response = view(request, service_request_id=service_request.id)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [service_request_attachments[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "service_request": ["This field is required."],
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
def test_service_request_attachment_create(
    api_rf,
    service_request_factory,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`maintenance.views.ServiceRequestAttachmentViewSet.create` method.
    """

    user = user_with_permissions([("maintenance", "servicerequestattachment")])
    service_request = service_request_factory(
        subscription=user.associated_subscription,
    )

    if status_code == 201:
        data["service_request"] = service_request.id

    with assertNumQueries(num_queries):
        url = reverse("maintenance:service_request_attachments-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = ServiceRequestAttachmentViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert ServiceRequestAttachment.objects.count() == obj_count


@pytest.mark.django_db
def test_service_request_attachment_retrieve(
    api_rf, service_request_attachment_factory, service_request_factory, user_with_permissions
):
    """
    Testing :py:meth:`maintenance.views.ServiceRequestAttachmentViewSet.retrieve` method.
    """

    user = user_with_permissions([("maintenance", "servicerequestattachment")])
    service_request_attachment = service_request_attachment_factory(
        subscription=user.associated_subscription,
    )

    with assertNumQueries(3):
        url = reverse(
            "maintenance:service_request_attachments-detail",
            kwargs={"pk": service_request_attachment.id},
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = ServiceRequestAttachmentViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=service_request_attachment.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "name",
        "created_by",
        "file",
        "service_request",
        "file_type",
        "updated_at",
    }


@pytest.mark.django_db
def test_service_request_attachment_update(
    api_rf, service_request_attachment_factory, user_with_permissions, service_request_factory
):
    """
    Testing :py:meth:`maintenance.views.ServiceRequestAttachmentViewSet.partial_update` method.
    """

    user = user_with_permissions([("maintenance", "servicerequestattachment")])
    service_request = service_request_factory(
        subscription=user.associated_subscription,
    )
    service_request_attachment = service_request_attachment_factory(
        subscription=user.associated_subscription,
    )
    data = {
        "service_request": service_request.id,
        "file": "Agreement.pdf",
        "name": "Agreement",
        "file_type": "pdf",
    }

    with assertNumQueries(5):
        url = reverse(
            "maintenance:service_request_attachments-detail",
            kwargs={"pk": service_request_attachment.id},
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = ServiceRequestAttachmentViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=service_request_attachment.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_service_request_attachment_delete(api_rf, service_request_attachment_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.ServiceRequestAttachmentViewSet.delete` method.
    """

    user = user_with_permissions([("maintenance", "servicerequestattachment")])
    service_request_attachment = service_request_attachment_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse(
            "maintenance:service_request_attachments-detail",
            kwargs={"pk": service_request_attachment.id},
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = ServiceRequestAttachmentViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=service_request_attachment.id)

    assert response.status_code == 204

    assert ServiceRequestAttachment.objects.count() == 0
