import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from property.models import RentableItem
from property.views import RentableItemViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"parent_property": 1}, [1, 0], 4),
    ),
)
@pytest.mark.django_db
def test_rentable_item_list(
    api_rf,
    query_params,
    index_result,
    num_queries,
    user_with_permissions,
    rentable_item_factory,
    property_factory,
):
    """
    Testing :py:meth:`property.views.RentableItemListAPIView` method.
    """
    user = user_with_permissions([("property", "rentableitem")])
    prop = property_factory(subscription=user.associated_subscription)

    if "parent_property" in query_params:
        query_params["parent_property"] = prop.id

    instance_1 = rentable_item_factory(parent_property=prop, subscription=user.associated_subscription)
    instance_2 = rentable_item_factory(parent_property=prop, subscription=user.associated_subscription)
    instance_3 = rentable_item_factory(subscription=user.associated_subscription)
    rentable_item_factory()

    rentable_items = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("property:rentable_items-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = RentableItemViewSet.as_view({"get": "list"})
        response = view(request, property_id=prop.id)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [rentable_items[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "amount": ["This field is required."],
                "gl_account": ["This field is required."],
                "tenant": ["This field is required."],
                "parent_property": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "name": "Parking",
                "description": "Parking",
                "amount": 100,
                "gl_account": "123",
                "status": True,
            },
            None,
            201,
            5,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_rentable_item_create(
    api_rf,
    property_factory,
    tenant_factory,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`property.views.RentableItemViewSet.create` method.
    """

    user = user_with_permissions([("property", "rentableitem")])
    prop = property_factory(subscription=user.associated_subscription)
    tenant = tenant_factory(subscription=user.associated_subscription)

    if status_code == 201:
        data["parent_property"] = prop.id
        data["tenant"] = tenant.id
    with assertNumQueries(num_queries):
        url = reverse("property:rentable_items-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = RentableItemViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert RentableItem.objects.count() == obj_count


@pytest.mark.django_db
def test_rentable_item_retrieve(api_rf, rentable_item_factory, user_with_permissions):
    """
    Testing :py:meth:`property.views.RentableItemViewSet.retrieve` method.
    """

    user = user_with_permissions([("property", "rentableitem")])
    rentable_item = rentable_item_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse(
            "property:rentable_items-detail",
            kwargs={"pk": rentable_item.id},
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = RentableItemViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=rentable_item.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "name",
        "description",
        "amount",
        "gl_account",
        "tenant",
        "status",
        "parent_property",
        "tenant_first_name",
        "tenant_last_name",
    }


@pytest.mark.django_db
def test_rentable_item_update(api_rf, rentable_item_factory, user_with_permissions, property_factory):
    """
    Testing :py:meth:`property.views.RentableItemViewSet.partial_update` method.
    """

    user = user_with_permissions([("property", "rentableitem")])
    prop = property_factory(subscription=user.associated_subscription)
    rentable_item = rentable_item_factory(subscription=user.associated_subscription)
    data = {
        "parent_property": prop.id,
        "name": "Parking",
        "description": "Parking",
        "amount": "100.00",
        "gl_account": "123",
        "status": True,
    }

    with assertNumQueries(5):
        url = reverse(
            "property:rentable_items-detail",
            kwargs={"pk": rentable_item.id},
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = RentableItemViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=rentable_item.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_rentable_item_delete(api_rf, rentable_item_factory, user_with_permissions):
    """
    Testing :py:meth:`property.views.RentableItemViewSet.delete` method.
    """

    user = user_with_permissions([("property", "rentableitem")])
    rentable_item = rentable_item_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse(
            "property:rentable_items-detail",
            kwargs={"pk": rentable_item.id},
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = RentableItemViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=rentable_item.id)

    assert response.status_code == 204

    assert RentableItem.objects.count() == 0
