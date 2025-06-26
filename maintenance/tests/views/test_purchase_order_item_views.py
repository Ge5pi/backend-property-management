import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from maintenance.models import PurchaseOrderItem
from maintenance.views import PurchaseOrderItemViewSet


@pytest.mark.django_db
def test_purchase_order_item_list(
    api_rf,
    user_with_permissions,
    purchase_order_item_factory,
):
    """
    Testing :py:meth:`maintenance.views.PurchaseOrderItemViewSet.list` method.
    """
    user = user_with_permissions([("maintenance", "purchaseorderitem")])
    instance_1 = purchase_order_item_factory(subscription=user.associated_subscription)
    instance_2 = purchase_order_item_factory(subscription=user.associated_subscription)
    instance_3 = purchase_order_item_factory(subscription=user.associated_subscription)
    purchase_order_item_factory()
    purchase_order_item_ids = [instance_1.id, instance_2.id, instance_3.id]
    index_result = [2, 1, 0]
    with assertNumQueries(6):
        url = reverse("maintenance:purchase_order_items-list")
        request = api_rf.get(url, {}, format="json")
        request.user = user
        view = PurchaseOrderItemViewSet.as_view({"get": "list"})
        response = view(request)
    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [purchase_order_item_ids[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "purchase_order": ["This field is required."],
                "inventory_item": ["This field is required."],
                "quantity": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "purchase_order": 100,
                "inventory_item": 100,
                "quantity": 9,
                "cost": "44.60",
            },
            None,
            201,
            5,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_purchase_order_item_create(
    api_rf,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
    inventory_factory,
    purchase_order_factory,
):
    """
    Testing :py:meth:`maintenance.views.PurchaseOrderItemViewSet.create` method.
    """
    user = user_with_permissions([("maintenance", "purchaseorderitem")])
    inventory_factory(id=100)
    purchase_order_factory(id=100)
    with assertNumQueries(num_queries):
        url = reverse("maintenance:purchase_order_items-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = PurchaseOrderItemViewSet.as_view({"post": "create"})
        response = view(request)
    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert PurchaseOrderItem.objects.count() == obj_count


@pytest.mark.django_db
def test_purchase_order_item_retrieve(api_rf, purchase_order_item_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.PurchaseOrderItemViewSet.retrieve` method.
    """
    user = user_with_permissions([("maintenance", "purchaseorderitem")])
    purchase_order_item = purchase_order_item_factory(subscription=user.associated_subscription)
    with assertNumQueries(4):
        url = reverse("maintenance:purchase_order_items-detail", kwargs={"pk": purchase_order_item.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = PurchaseOrderItemViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=purchase_order_item.id)
    assert response.status_code == 200
    assert response.data.keys() == {
        "id",
        "inventory_item_name",
        "inventory_item",
        "quantity",
        "cost",
        "purchase_order",
        "total_cost",
        "tax_value",
        "discount_value",
        "item_cost",
    }


@pytest.mark.django_db
def test_purchase_order_item_update(
    api_rf,
    purchase_order_item_factory,
    user_with_permissions,
    inventory_factory,
    purchase_order_factory,
):
    """
    Testing :py:meth:`maintenance.views.PurchaseOrderItemViewSet.partial_update` method.
    """
    user = user_with_permissions([("maintenance", "purchaseorderitem")])
    inventory_factory(id=100)
    purchase_order_factory(id=100)
    purchase_order_item = purchase_order_item_factory(subscription=user.associated_subscription)
    data = {
        "purchase_order": 100,
        "inventory_item": 100,
        "quantity": 9,
    }
    with assertNumQueries(6):
        url = reverse("maintenance:purchase_order_items-detail", kwargs={"pk": purchase_order_item.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = PurchaseOrderItemViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=purchase_order_item.id)
    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_purchase_order_item_delete(api_rf, purchase_order_item_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.PurchaseOrderItemViewSet.delete` method.
    """
    user = user_with_permissions([("maintenance", "purchaseorderitem")])
    purchase_order_item = purchase_order_item_factory(subscription=user.associated_subscription)
    with assertNumQueries(4):
        url = reverse("maintenance:purchase_order_items-detail", kwargs={"pk": purchase_order_item.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = PurchaseOrderItemViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=purchase_order_item.id)
    assert response.status_code == 204
    assert PurchaseOrderItem.objects.count() == 0


@pytest.mark.django_db
def test_purchase_order_item_list_by_purchase_order(
    api_rf,
    user_with_permissions,
    purchase_order_factory,
    purchase_order_item_factory,
):
    """
    Testing :py:meth:`maintenance.views.PurchaseOrderItemViewSet.list` method.
    """
    user = user_with_permissions([("maintenance", "purchaseorderitem")])
    purchase_order = purchase_order_factory()
    instance_1 = purchase_order_item_factory(purchase_order=purchase_order, subscription=user.associated_subscription)
    instance_2 = purchase_order_item_factory(purchase_order=purchase_order, subscription=user.associated_subscription)
    instance_3 = purchase_order_item_factory(purchase_order=purchase_order, subscription=user.associated_subscription)

    purchase_order_item_ids = [instance_1.id, instance_2.id, instance_3.id]
    index_result = [2, 1, 0]

    with assertNumQueries(6):
        url = reverse("maintenance:items-by-purchase-order", kwargs={"purchase_order_id": purchase_order.id})
        request = api_rf.get(url, {}, format="json")
        request.user = user
        view = PurchaseOrderItemViewSet.as_view({"get": "list"})
        response = view(request, purchase_order_id=purchase_order.id)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [purchase_order_item_ids[i] for i in index_result]
