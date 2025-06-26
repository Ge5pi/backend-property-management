import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from people.models import OwnerUpcomingActivity
from people.views import OwnerUpcomingActivityViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"owner": 1}, [2, 1], 4),
        ({"title": "lorem"}, [0], 3),
        ({"date_month": "02"}, [2, 1], 3),
        ({"date_year": "2023"}, [0], 3),
        ({"label_id": True}, [0], 3),
    ),
)
@pytest.mark.django_db
def test_owner_upcoming_activity_list(
    api_rf,
    user_with_permissions,
    owner_upcoming_activity_factory,
    query_params,
    index_result,
    num_queries,
    owner_people_factory,
    label_factory,
):
    """
    Testing :py:meth:`people.views.OwnerUpcomingActivityViewSet.list` method.
    """
    user = user_with_permissions([("people", "ownerupcomingactivity")])
    owner = owner_people_factory(subscription=user.associated_subscription)

    label_1 = label_factory(subscription=user.associated_subscription)
    label_2 = label_factory(subscription=user.associated_subscription)

    if "label_id" in query_params:
        query_params["label_id"] = f"{label_1.id},{label_2.id}"

    if "owner" in query_params:
        query_params["owner"] = owner.id

    owner_upcoming_activity_1 = owner_upcoming_activity_factory(
        title="lorem", subscription=user.associated_subscription, date="2023-01-01", label=label_1
    )
    owner_upcoming_activity_2 = owner_upcoming_activity_factory(
        owner=owner, title="ipsum", subscription=user.associated_subscription, date="2024-02-02"
    )
    owner_upcoming_activity_3 = owner_upcoming_activity_factory(
        owner=owner, title="dolor", subscription=user.associated_subscription, date="2024-02-03"
    )
    owner_upcoming_activity_factory()

    owner_upcoming_activities = [
        owner_upcoming_activity_1.id,
        owner_upcoming_activity_2.id,
        owner_upcoming_activity_3.id,
    ]

    with assertNumQueries(num_queries):
        url = reverse("people:owner_upcoming_activity-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = OwnerUpcomingActivityViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [owner_upcoming_activities[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "title": ["This field is required."],
                "date": ["This field is required."],
                "owner": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "title": "lorem ipsum",
                "description": "lorem ipsum dolor",
                "date": "1977-08-31",
                "start_time": "14:23:03",
                "end_time": "14:23:03",
                "label": 1,
                "assign_to": 1,
                "status": False,
                "owner": 1,
            },
            None,
            201,
            6,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_owner_upcoming_activity_create(
    api_rf,
    owner_people_factory,
    label_factory,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`people.views.OwnerUpcomingActivityViewSet.create` method.
    """

    user = user_with_permissions([("people", "ownerupcomingactivity")])
    owner = owner_people_factory()
    label = label_factory()

    if status_code == 201:
        data["owner"] = owner.id
        data["label"] = label.id
        data["assign_to"] = user.id

    with assertNumQueries(num_queries):
        url = reverse("people:owner_upcoming_activity-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = OwnerUpcomingActivityViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert OwnerUpcomingActivity.objects.count() == obj_count


@pytest.mark.django_db
def test_owner_upcoming_activity_retrieve(api_rf, owner_upcoming_activity_factory, user_with_permissions):
    """
    Testing :py:meth:`people.views.OwnerUpcomingActivityViewSet.retrieve` method.
    """

    user = user_with_permissions([("people", "ownerupcomingactivity")])
    owner_upcoming_activity = owner_upcoming_activity_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse("people:owner_upcoming_activity-detail", kwargs={"pk": owner_upcoming_activity.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = OwnerUpcomingActivityViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=owner_upcoming_activity.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "title",
        "description",
        "date",
        "start_time",
        "end_time",
        "label",
        "assign_to",
        "status",
        "owner",
        "label_name",
        "assign_to_first_name",
        "assign_to_last_name",
        "assign_to_username",
        "owner_first_name",
        "owner_last_name",
    }


@pytest.mark.django_db
def test_owner_upcoming_activity_update(api_rf, owner_upcoming_activity_factory, user_with_permissions):
    """
    Testing :py:meth:`people.views.OwnerUpcomingActivityViewSet.partial_update` method.
    """

    user = user_with_permissions([("people", "ownerupcomingactivity")])
    owner_upcoming_activity = owner_upcoming_activity_factory(subscription=user.associated_subscription)
    data = {
        "title": "lorem ipsum",
        "description": "lorem ipsum dolor",
        "date": "1977-08-31",
        "start_time": "14:23:03",
        "end_time": "14:23:03",
        "label": owner_upcoming_activity.label.id,
        "assign_to": owner_upcoming_activity.assign_to.id,
        "status": False,
        "owner": owner_upcoming_activity.owner.id,
    }

    with assertNumQueries(7):
        url = reverse("people:owner_upcoming_activity-detail", kwargs={"pk": owner_upcoming_activity.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = OwnerUpcomingActivityViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=owner_upcoming_activity.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_owner_upcoming_activity_delete(api_rf, owner_upcoming_activity_factory, user_with_permissions):
    """
    Testing :py:meth:`people.views.OwnerUpcomingActivityViewSet.delete` method.
    """

    user = user_with_permissions([("people", "ownerupcomingactivity")])
    owner_upcoming_activity = owner_upcoming_activity_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse(
            "people:owner_upcoming_activity-detail",
            kwargs={
                "pk": owner_upcoming_activity.id,
            },
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = OwnerUpcomingActivityViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=owner_upcoming_activity.id)

    assert response.status_code == 204

    assert OwnerUpcomingActivity.objects.count() == 0
