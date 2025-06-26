from datetime import date

import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from maintenance.models import Inspection
from maintenance.views import InspectionViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 12),
        ({"search": "cost go major"}, [0], 6),
        ({"ordering": "name"}, [0, 1, 2], 12),
        ({"ordering": "-name"}, [2, 1, 0], 12),
        ({"ordering": "date"}, [0, 1, 2], 12),
        ({"ordering": "-date"}, [2, 1, 0], 12),
        ({"unit": 0}, [0], 7),
        ({"date__lte": "2023-1-2"}, [1, 0], 9),
        ({"date__gte": "2023-1-2"}, [2, 1], 9),
    ),
)
@pytest.mark.django_db
def test_inspection_list(
    api_rf, user_with_permissions, unit_factory, inspection_factory, query_params, index_result, num_queries
):
    """
    Testing :py:meth:`maintenance.views.InspectionViewSet.list` method.
    """
    user = user_with_permissions([("maintenance", "inspection")])
    unit = unit_factory()

    if "unit" in query_params:
        query_params["unit"] = unit.id

    instance_1 = inspection_factory(
        name="Actually cost go major", date=date(2023, 1, 1), unit=unit, subscription=user.associated_subscription
    )
    instance_2 = inspection_factory(
        name="Author simple bed", date=date(2023, 1, 2), subscription=user.associated_subscription
    )
    instance_3 = inspection_factory(
        name="Food inside interesting else know task", date=date(2023, 1, 3), subscription=user.associated_subscription
    )
    inspection_factory()

    inspections = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("maintenance:inspection-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = InspectionViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [inspections[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "date": ["This field is required."],
                "unit": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "name": "Fan",
                "date": "2020-01-01",
                "unit": 1,
            },
            None,
            201,
            7,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_inspection_create(
    api_rf, user_with_permissions, unit_factory, data, expected_response, status_code, num_queries, obj_count
):
    """
    Testing :py:meth:`maintenance.views.InspectionViewSet.create` method.
    """

    user = user_with_permissions([("maintenance", "inspection")])
    unit = unit_factory()

    if status_code == 201:
        data["unit"] = unit.id

    with assertNumQueries(num_queries):
        url = reverse("maintenance:inspection-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = InspectionViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert Inspection.objects.count() == obj_count


@pytest.mark.django_db
def test_inspection_retrieve(api_rf, inspection_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.InspectionViewSet.retrieve` method.
    """

    user = user_with_permissions([("maintenance", "inspection")])
    inspection = inspection_factory(subscription=user.associated_subscription)

    with assertNumQueries(6):
        url = reverse("maintenance:inspection-detail", kwargs={"pk": inspection.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = InspectionViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=inspection.id)

    assert response.status_code == 200

    assert response.data.keys() == {"id", "name", "date", "unit", "unit_name", "property_name", "unit_cover_picture"}


@pytest.mark.django_db
def test_inspection_update(api_rf, inspection_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.InspectionViewSet.partial_update` method.
    """

    user = user_with_permissions([("maintenance", "inspection")])
    inspection = inspection_factory(subscription=user.associated_subscription)
    data = {
        "name": "Fan",
        "date": "2020-01-01",
        "unit": inspection.unit.id,
    }

    with assertNumQueries(8):
        url = reverse("maintenance:inspection-detail", kwargs={"pk": inspection.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = InspectionViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=inspection.id)

    assert response.status_code == 200

    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_inspection_delete(api_rf, inspection_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.InspectionViewSet.delete` method.
    """

    user = user_with_permissions([("maintenance", "inspection")])
    inspection = inspection_factory(subscription=user.associated_subscription)

    with assertNumQueries(5):
        url = reverse("maintenance:inspection-detail", kwargs={"pk": inspection.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = InspectionViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=inspection.id)

    assert response.status_code == 204

    assert Inspection.objects.count() == 0
