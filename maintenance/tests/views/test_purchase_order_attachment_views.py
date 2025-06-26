import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from maintenance.models import PurchaseOrderAttachment
from maintenance.views import PurchaseOrderAttachmentViewSet


@pytest.mark.django_db
def test_purchase_order_attachment_list(
    api_rf,
    user_with_permissions,
    purchase_order_attachment_factory,
):
    """
    Testing :py:meth:`maintenance.views.PurchaseOrderAttachmentViewSet.list` method.
    """
    user = user_with_permissions([("maintenance", "purchaseorderattachment")])
    instance_1 = purchase_order_attachment_factory(subscription=user.associated_subscription)
    instance_2 = purchase_order_attachment_factory(subscription=user.associated_subscription)
    instance_3 = purchase_order_attachment_factory(subscription=user.associated_subscription)
    purchase_order_attachment_factory()
    purchase_order_attachment_ids = [instance_1.id, instance_2.id, instance_3.id]
    index_result = [2, 1, 0]
    with assertNumQueries(3):
        url = reverse("maintenance:purchase_order_attachments-list")
        request = api_rf.get(url, {}, format="json")
        request.user = user
        view = PurchaseOrderAttachmentViewSet.as_view({"get": "list"})
        response = view(request)
    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [purchase_order_attachment_ids[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "purchase_order": ["This field is required."],
                "name": ["This field is required."],
                "file": ["This field is required."],
                "file_type": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "purchase_order": 100,
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
def test_purchase_order_attachment_create(
    api_rf,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
    purchase_order_factory,
):
    """
    Testing :py:meth:`maintenance.views.PurchaseOrderAttachmentViewSet.create` method.
    """
    user = user_with_permissions([("maintenance", "purchaseorderattachment")])
    purchase_order_factory(id=100)
    with assertNumQueries(num_queries):
        url = reverse("maintenance:purchase_order_attachments-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = PurchaseOrderAttachmentViewSet.as_view({"post": "create"})
        response = view(request)
    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert PurchaseOrderAttachment.objects.count() == obj_count


@pytest.mark.django_db
def test_purchase_order_attachment_retrieve(api_rf, purchase_order_attachment_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.PurchaseOrderAttachmentViewSet.retrieve` method.
    """
    user = user_with_permissions([("maintenance", "purchaseorderattachment")])
    purchase_order_attachment = purchase_order_attachment_factory(subscription=user.associated_subscription)
    with assertNumQueries(3):
        url = reverse(
            "maintenance:purchase_order_attachments-detail",
            kwargs={"pk": purchase_order_attachment.id},
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = PurchaseOrderAttachmentViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=purchase_order_attachment.id)
    assert response.status_code == 200
    assert response.data.keys() == {
        "id",
        "name",
        "created_by",
        "file",
        "purchase_order",
        "file_type",
        "updated_at",
    }


@pytest.mark.django_db
def test_purchase_order_attachment_update(
    api_rf,
    purchase_order_attachment_factory,
    user_with_permissions,
    purchase_order_factory,
):
    """
    Testing :py:meth:`maintenance.views.PurchaseOrderAttachmentViewSet.partial_update` method.
    """
    user = user_with_permissions([("maintenance", "purchaseorderattachment")])
    purchase_order_factory(id=100)
    purchase_order_attachment = purchase_order_attachment_factory(subscription=user.associated_subscription)
    data = {
        "purchase_order": 100,
        "file": "Agreement.pdf",
        "name": "Agreement",
        "file_type": "pdf",
    }
    with assertNumQueries(5):
        url = reverse(
            "maintenance:purchase_order_attachments-detail",
            kwargs={"pk": purchase_order_attachment.id},
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = PurchaseOrderAttachmentViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=purchase_order_attachment.id)
    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_purchase_order_attachment_delete(api_rf, purchase_order_attachment_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.PurchaseOrderAttachmentViewSet.delete` method.
    """
    user = user_with_permissions([("maintenance", "purchaseorderattachment")])
    purchase_order_attachment = purchase_order_attachment_factory(subscription=user.associated_subscription)
    with assertNumQueries(4):
        url = reverse(
            "maintenance:purchase_order_attachments-detail",
            kwargs={"pk": purchase_order_attachment.id},
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = PurchaseOrderAttachmentViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=purchase_order_attachment.id)
    assert response.status_code == 204
    assert PurchaseOrderAttachment.objects.count() == 0


@pytest.mark.django_db
def test_purchase_order_attachment_list_by_purchase_order(
    api_rf,
    user_with_permissions,
    purchase_order_factory,
    purchase_order_attachment_factory,
):
    """
    Testing :py:meth:`maintenance.views.PurchaseOrderAttachmentViewSet.list` method.
    """
    user = user_with_permissions([("maintenance", "purchaseorderattachment")])
    purchase_order = purchase_order_factory(subscription=user.associated_subscription)

    instance_1 = purchase_order_attachment_factory(
        purchase_order=purchase_order, subscription=user.associated_subscription
    )
    instance_2 = purchase_order_attachment_factory(
        purchase_order=purchase_order, subscription=user.associated_subscription
    )
    instance_3 = purchase_order_attachment_factory(
        purchase_order=purchase_order, subscription=user.associated_subscription
    )

    purchase_order_attachment_ids = [instance_1.id, instance_2.id, instance_3.id]
    index_result = [2, 1, 0]

    with assertNumQueries(3):
        url = reverse(
            "maintenance:attachments-by-purchase-order",
            kwargs={"purchase_order_id": purchase_order.id},
        )
        request = api_rf.get(url, {}, format="json")
        request.user = user
        view = PurchaseOrderAttachmentViewSet.as_view({"get": "list"})
        response = view(request, purchase_order_id=purchase_order.id)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [purchase_order_attachment_ids[i] for i in index_result]
