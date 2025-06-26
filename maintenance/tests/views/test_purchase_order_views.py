import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from maintenance.models import PurchaseOrder
from maintenance.views import PurchaseOrderViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 6),
        ({"search": "FirstName John"}, [2], 4),
        ({"search": "LastName Smith"}, [2], 4),
        ({"search": "success thus yourself treatment"}, [0], 4),
        ({"vendor": 0}, [2], 5),
        ({"total_less_than_equal": 100}, [2, 1], 5),
        ({"total_greater_than_equal": 1000}, [0], 4),
    ),
)
@pytest.mark.django_db
def test_purchase_order_list(
    api_rf,
    user_with_permissions,
    purchase_order_factory,
    purchase_order_item_factory,
    inventory_factory,
    vendor_factory,
    query_params,
    index_result,
    num_queries,
):
    """
    Testing :py:meth:`maintenance.views.PurchaseOrderViewSet.list` method.
    """
    user = user_with_permissions([("maintenance", "purchaseorder")])
    vendor = vendor_factory(first_name="FirstName John", last_name="LastName Smith")

    if "vendor" in query_params:
        query_params["vendor"] = vendor.id

    instance_1 = purchase_order_factory(
        description="Short success thus yourself treatment condition often.",
        tax=10,
        shipping=10,
        discount=5,
        subscription=user.associated_subscription,
    )
    instance_2 = purchase_order_factory(
        tax=10,
        shipping=0,
        discount=0,
        subscription=user.associated_subscription,
    )
    instance_3 = purchase_order_factory(
        vendor=vendor, tax=10, shipping=0, discount=0, subscription=user.associated_subscription
    )
    purchase_order_factory()
    inventory_item = inventory_factory(cost="100")
    purchase_order_item_factory(purchase_order=instance_1, quantity=10, inventory_item=inventory_item)

    purchase_order_ids = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("maintenance:purchase_orders-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = PurchaseOrderViewSet.as_view({"get": "list"})
        response = view(request)

    response_ids = [i["id"] for i in response.data]
    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    assert response_ids == [purchase_order_ids[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "description": ["This field is required."],
                "required_by_date": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "vendor": 100,
                "description": "Read line shake short term. Generation fine hotel word in religious energy.",
                "required_by_date": "2020-01-01",
                "tax": "10",
                "tax_charge_type": "FLAT",
                "shipping": "10",
                "shipping_charge_type": "FLAT",
                "discount": "10",
                "discount_charge_type": "PERCENT",
                "notes": "Read line shake short term. Generation fine hotel word in religious energy.",
            },
            None,
            201,
            4,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_purchase_order_create(
    api_rf, user_with_permissions, data, expected_response, status_code, num_queries, obj_count, vendor_factory
):
    """
    Testing :py:meth:`maintenance.views.PurchaseOrderViewSet.create` method.
    """
    user = user_with_permissions([("maintenance", "purchaseorder")])
    vendor_factory(id=100, first_name="Joanna", last_name="Brennan")

    with assertNumQueries(num_queries):
        url = reverse("maintenance:purchase_orders-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = PurchaseOrderViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert PurchaseOrder.objects.count() == obj_count


@pytest.mark.django_db
def test_purchase_order_retrieve(api_rf, purchase_order_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.PurchaseOrderViewSet.retrieve` method.
    """
    user = user_with_permissions([("maintenance", "purchaseorder")])
    purchase_order = purchase_order_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse("maintenance:purchase_orders-detail", kwargs={"pk": purchase_order.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = PurchaseOrderViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=purchase_order.id)

    assert response.status_code == 200
    assert response.data.keys() == {
        "id",
        "slug",
        "vendor",
        "description",
        "required_by_date",
        "tax",
        "tax_charge_type",
        "get_tax_charge_type_display",
        "shipping",
        "shipping_charge_type",
        "get_shipping_charge_type_display",
        "discount",
        "discount_charge_type",
        "get_discount_charge_type_display",
        "notes",
        "vendor_first_name",
        "vendor_last_name",
        "sub_total",
        "tax_value",
        "discount_value",
        "shipping_value",
        "total",
        "created_at",
    }


@pytest.mark.django_db
def test_purchase_order_update(api_rf, purchase_order_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.PurchaseOrderViewSet.partial_update` method.
    """
    user = user_with_permissions([("maintenance", "purchaseorder")])
    purchase_order = purchase_order_factory(subscription=user.associated_subscription)
    data = {
        "vendor": purchase_order.vendor.id,
        "description": "Read line shake short term. Generation fine hotel word in religious energy.",
        "required_by_date": "2020-01-01",
        "tax": "10.00",
        "tax_charge_type": "FLAT",
        "shipping": "10.00",
        "shipping_charge_type": "FLAT",
        "discount": "10.00",
        "discount_charge_type": "PERCENT",
        "notes": "Read line shake short term. Generation fine hotel word in religious energy.",
    }

    with assertNumQueries(5):
        url = reverse("maintenance:purchase_orders-detail", kwargs={"pk": purchase_order.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = PurchaseOrderViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=purchase_order.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_purchase_order_delete(api_rf, purchase_order_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.PurchaseOrderViewSet.delete` method.
    """
    user = user_with_permissions([("maintenance", "purchaseorder")])
    purchase_order = purchase_order_factory(subscription=user.associated_subscription)

    with assertNumQueries(6):
        url = reverse("maintenance:purchase_orders-detail", kwargs={"pk": purchase_order.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = PurchaseOrderViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=purchase_order.id)

    assert response.status_code == 204
    assert PurchaseOrder.objects.count() == 0
