import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from maintenance.models import Area
from maintenance.views import AreaViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"search": "cost go major"}, [0], 3),
        ({"inspection": 0}, [0], 4),
    ),
)
@pytest.mark.django_db
def test_area_list(
    api_rf, user_with_permissions, inspection_factory, area_factory, query_params, index_result, num_queries
):
    """
    Testing :py:meth:`maintenance.views.AreaViewSet.list` method.
    """
    user = user_with_permissions([("maintenance", "area")])
    inspection = inspection_factory()

    if "inspection" in query_params:
        query_params["inspection"] = inspection.id

    instance_1 = area_factory(
        name="Actually cost go major", inspection=inspection, subscription=user.associated_subscription
    )
    instance_2 = area_factory(name="Author simple bed", subscription=user.associated_subscription)
    instance_3 = area_factory(name="Food inside interesting else know task", subscription=user.associated_subscription)
    area_factory()

    areas = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("maintenance:area-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = AreaViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [areas[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "inspection": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {"name": "Fan"},
            None,
            201,
            4,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_area_create(
    api_rf, user_with_permissions, inspection_factory, data, expected_response, status_code, num_queries, obj_count
):
    """
    Testing :py:meth:`maintenance.views.AreaViewSet.create` method.
    """

    user = user_with_permissions([("maintenance", "area")])
    inspection = inspection_factory()

    if status_code == 201:
        data["inspection"] = inspection.id

    with assertNumQueries(num_queries):
        url = reverse("maintenance:area-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = AreaViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert Area.objects.count() == obj_count


@pytest.mark.django_db
def test_area_retrieve(api_rf, area_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.AreaViewSet.retrieve` method.
    """

    user = user_with_permissions([("maintenance", "area")])
    area = area_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse("maintenance:area-detail", kwargs={"pk": area.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = AreaViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=area.id)

    assert response.status_code == 200

    assert response.data.keys() == {"id", "name", "inspection"}


@pytest.mark.django_db
def test_area_update(api_rf, area_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.AreaViewSet.partial_update` method.
    """

    user = user_with_permissions([("maintenance", "area")])
    area = area_factory(subscription=user.associated_subscription)
    data = {
        "name": "Fan",
        "inspection": area.inspection.id,
    }

    with assertNumQueries(5):
        url = reverse("maintenance:area-detail", kwargs={"pk": area.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = AreaViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=area.id)

    assert response.status_code == 200

    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_area_delete(api_rf, area_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.AreaViewSet.delete` method.
    """

    user = user_with_permissions([("maintenance", "area")])
    area = area_factory(subscription=user.associated_subscription)

    with assertNumQueries(5):
        url = reverse("maintenance:area-detail", kwargs={"pk": area.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = AreaViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=area.id)

    assert response.status_code == 204

    assert Area.objects.count() == 0
