import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from maintenance.models import Labor
from maintenance.views import LaborViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"search": "cost go major"}, [0], 3),
        ({"search": "inside interesting else"}, [2], 3),
        ({"ordering": "title"}, [0, 1, 2], 3),
        ({"ordering": "-title"}, [2, 1, 0], 3),
        ({"work_order": 1}, [0], 4),
    ),
)
@pytest.mark.django_db
def test_labor_list(
    api_rf, user_with_permissions, work_order_factory, labor_factory, query_params, index_result, num_queries
):
    """
    Testing :py:meth:`maintenance.views.LaborViewSet.list` method.
    """
    user = user_with_permissions([("maintenance", "labor")])
    work_order = work_order_factory()

    if "work_order" in query_params:
        query_params["work_order"] = work_order.id

    instance_1 = labor_factory(
        title="Actually cost go major",
        description="Sing democratic decade",
        work_order=work_order,
        subscription=user.associated_subscription,
    )
    instance_2 = labor_factory(
        title="Author simple bed", description="popular right crime hotel", subscription=user.associated_subscription
    )
    instance_3 = labor_factory(
        title="Food inside interesting else know task",
        description="What lot yeah benefit",
        subscription=user.associated_subscription,
    )
    labor_factory()

    labors = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("maintenance:labor-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = LaborViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [labors[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "title": ["This field is required."],
                "description": ["This field is required."],
                "date": ["This field is required."],
                "hours": ["This field is required."],
                "work_order": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "title": "Fan",
                "description": "Read line shake short term.",
                "date": "2020-01-01",
                "hours": 9,
            },
            None,
            201,
            4,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_labor_create(
    api_rf, user_with_permissions, work_order_factory, data, expected_response, status_code, num_queries, obj_count
):
    """
    Testing :py:meth:`maintenance.views.LaborViewSet.create` method.
    """

    user = user_with_permissions([("maintenance", "labor")])
    work_order = work_order_factory()

    if status_code == 201:
        data["work_order"] = work_order.id

    with assertNumQueries(num_queries):
        url = reverse("maintenance:labor-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = LaborViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert Labor.objects.count() == obj_count


@pytest.mark.django_db
def test_labor_retrieve(api_rf, labor_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.LaborViewSet.retrieve` method.
    """

    user = user_with_permissions([("maintenance", "labor")])
    labor = labor_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse("maintenance:labor-detail", kwargs={"pk": labor.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = LaborViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=labor.id)

    assert response.status_code == 200

    assert response.data.keys() == {"id", "title", "date", "hours", "description", "work_order"}


@pytest.mark.django_db
def test_labor_update(api_rf, labor_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.LaborViewSet.partial_update` method.
    """

    user = user_with_permissions([("maintenance", "labor")])
    labor = labor_factory(subscription=user.associated_subscription)
    data = {
        "title": "Fan",
        "description": "Read line shake short term.",
        "date": "2020-01-01",
        "hours": 9,
        "work_order": labor.work_order.id,
    }

    with assertNumQueries(5):
        url = reverse("maintenance:labor-detail", kwargs={"pk": labor.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = LaborViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=labor.id)

    assert response.status_code == 200

    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_labor_delete(api_rf, labor_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.LaborViewSet.delete` method.
    """

    user = user_with_permissions([("maintenance", "labor")])
    labor = labor_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse("maintenance:labor-detail", kwargs={"pk": labor.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = LaborViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=labor.id)

    assert response.status_code == 204

    assert Labor.objects.count() == 0
