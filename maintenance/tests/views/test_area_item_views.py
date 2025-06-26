import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from maintenance.models import AreaItem
from maintenance.views import AreaItemViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"area": 0}, [0], 4),
    ),
)
@pytest.mark.django_db
def test_area_item_list(
    api_rf, user_with_permissions, area_factory, area_item_factory, query_params, index_result, num_queries
):
    """
    Testing :py:meth:`maintenance.views.AreaItemViewSet.list` method.
    """
    user = user_with_permissions([("maintenance", "areaitem")])
    area = area_factory()

    if "area" in query_params:
        query_params["area"] = area.id

    instance_1 = area_item_factory(name="Actually cost go major", area=area, subscription=user.associated_subscription)
    instance_2 = area_item_factory(name="Author simple bed", subscription=user.associated_subscription)
    instance_3 = area_item_factory(
        name="Food inside interesting else know task", subscription=user.associated_subscription
    )
    area_item_factory()

    area_items = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("maintenance:area_item-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = AreaItemViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [area_items[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "condition": ["This field is required."],
                "area": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {"name": "Fan", "condition": "OKAY"},
            None,
            201,
            4,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_area_item_create(
    api_rf, user_with_permissions, area_factory, data, expected_response, status_code, num_queries, obj_count
):
    """
    Testing :py:meth:`maintenance.views.AreaItemViewSet.create` method.
    """

    user = user_with_permissions([("maintenance", "areaitem")])
    area = area_factory()

    if status_code == 201:
        data["area"] = area.id

    with assertNumQueries(num_queries):
        url = reverse("maintenance:area_item-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = AreaItemViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert AreaItem.objects.count() == obj_count


@pytest.mark.django_db
def test_area_item_retrieve(api_rf, area_item_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.AreaItemViewSet.retrieve` method.
    """

    user = user_with_permissions([("maintenance", "areaitem")])
    area_item = area_item_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse("maintenance:area_item-detail", kwargs={"pk": area_item.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = AreaItemViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=area_item.id)

    assert response.status_code == 200

    assert response.data.keys() == {"id", "name", "condition", "get_condition_display", "area"}


@pytest.mark.django_db
def test_area_item_update(api_rf, area_item_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.AreaItemViewSet.partial_update` method.
    """

    user = user_with_permissions([("maintenance", "areaitem")])
    area_item = area_item_factory(subscription=user.associated_subscription)
    data = {
        "name": "Fan",
        "condition": "OKAY",
        "area": area_item.area.id,
    }

    with assertNumQueries(5):
        url = reverse("maintenance:area_item-detail", kwargs={"pk": area_item.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = AreaItemViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=area_item.id)

    assert response.status_code == 200

    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_area_item_delete(api_rf, area_item_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.AreaItemViewSet.delete` method.
    """

    user = user_with_permissions([("maintenance", "areaitem")])
    area_item = area_item_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse("maintenance:area_item-detail", kwargs={"pk": area_item.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = AreaItemViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=area_item.id)

    assert response.status_code == 204

    assert AreaItem.objects.count() == 0
