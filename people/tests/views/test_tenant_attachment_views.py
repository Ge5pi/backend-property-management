import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from people.models import TenantAttachment
from people.views import TenantAttachmentViewSet


@pytest.mark.django_db
def test_tenant_attachment_list(
    api_rf,
    user_with_permissions,
    tenant_attachment_factory,
    tenant_factory,
):
    """
    Testing :py:meth:`people.views.TenantAttachmentViewSet.list` method.
    """
    user = user_with_permissions([("people", "tenantattachment")])

    tenant = tenant_factory()
    tenant_attachment_1 = tenant_attachment_factory(tenant=tenant, subscription=user.associated_subscription)
    tenant_attachment_2 = tenant_attachment_factory(tenant=tenant, subscription=user.associated_subscription)
    tenant_attachment_3 = tenant_attachment_factory(tenant=tenant, subscription=user.associated_subscription)
    tenant_attachment_factory()

    tenant_attachments = [
        tenant_attachment_1.id,
        tenant_attachment_2.id,
        tenant_attachment_3.id,
    ]
    index_result = [2, 1, 0]

    with assertNumQueries(3):
        url = reverse("people:tenant_attachment-list", kwargs={"tenant_id": tenant.id})
        request = api_rf.get(url, {}, format="json")
        request.user = user
        view = TenantAttachmentViewSet.as_view({"get": "list"})
        response = view(request, tenant_id=tenant.id)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [tenant_attachments[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "file": ["This field is required."],
                "tenant": ["This field is required."],
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
def test_tenant_attachment_create(
    api_rf,
    tenant_factory,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`people.views.TenantAttachmentViewSet.create` method.
    """

    user = user_with_permissions([("people", "tenantattachment")])
    tenant = tenant_factory()

    if status_code == 201:
        data["tenant"] = tenant.id

    with assertNumQueries(num_queries):
        url = reverse("people:tenant_attachment-list", kwargs={"tenant_id": tenant.id})
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = TenantAttachmentViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert TenantAttachment.objects.count() == obj_count


@pytest.mark.django_db
def test_tenant_attachment_retrieve(api_rf, tenant_attachment_factory, user_with_permissions):
    """
    Testing :py:meth:`people.views.TenantAttachmentViewSet.retrieve` method.
    """

    user = user_with_permissions([("people", "tenantattachment")])
    tenant_attachment = tenant_attachment_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse(
            "people:tenant_attachment-detail",
            kwargs={
                "pk": tenant_attachment.id,
                "tenant_id": tenant_attachment.tenant.id,
            },
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = TenantAttachmentViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=tenant_attachment.id, tenant_id=tenant_attachment.tenant.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "name",
        "created_by",
        "file",
        "tenant",
        "file_type",
        "updated_at",
    }


@pytest.mark.django_db
def test_tenant_attachment_update(api_rf, tenant_attachment_factory, user_with_permissions, tenant_factory):
    """
    Testing :py:meth:`people.views.TenantAttachmentViewSet.partial_update` method.
    """

    user = user_with_permissions([("people", "tenantattachment")])
    tenant_attachment = tenant_attachment_factory(subscription=user.associated_subscription)
    data = {
        "tenant": tenant_attachment.tenant.id,
        "file": "Agreement.pdf",
        "name": "Agreement",
        "file_type": "pdf",
    }

    with assertNumQueries(5):
        url = reverse(
            "people:tenant_attachment-detail",
            kwargs={
                "pk": tenant_attachment.id,
                "tenant_id": tenant_attachment.tenant.id,
            },
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = TenantAttachmentViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=tenant_attachment.id, tenant_id=tenant_attachment.tenant.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_tenant_attachment_delete(api_rf, tenant_attachment_factory, user_with_permissions):
    """
    Testing :py:meth:`people.views.TenantAttachmentViewSet.delete` method.
    """

    user = user_with_permissions([("people", "tenantattachment")])
    tenant_attachment = tenant_attachment_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse(
            "people:tenant_attachment-detail",
            kwargs={
                "pk": tenant_attachment.id,
                "tenant_id": tenant_attachment.tenant.id,
            },
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = TenantAttachmentViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=tenant_attachment.id, tenant_id=tenant_attachment.tenant.id)

    assert response.status_code == 204

    assert TenantAttachment.objects.count() == 0
