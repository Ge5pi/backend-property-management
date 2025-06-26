from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from pytest_django.asserts import assertNumQueries

from communication.models import Announcement
from communication.views import AnnouncementUnitsListAPIView, AnnouncementViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 5),
        ({"search": "heavy great"}, [0], 5),
        ({"search": "toward"}, [1, 0], 5),
        ({"search": "seek better"}, [1], 5),
        ({"ordering": "title"}, [0, 2, 1], 5),
        ({"ordering": "-title"}, [1, 2, 0], 5),
        ({"ordering": "created_at"}, [0, 1, 2], 5),
        ({"ordering": "-created_at"}, [2, 1, 0], 5),
        ({"ordering": "pk"}, [0, 1, 2], 5),
        ({"ordering": "-pk"}, [2, 1, 0], 5),
        ({"properties": 300}, [2, 0], 6),
        ({"units": 100}, [1], 6),
        ({"status": "Active"}, [0], 5),
        ({"status": "Expired"}, [2, 1], 5),
    ),
)
@pytest.mark.django_db
def test_announcement_list(
    api_rf,
    user_with_permissions,
    announcement_factory,
    property_factory,
    unit_factory,
    query_params,
    index_result,
    num_queries,
):
    """
    Testing :py:meth:`communication.views.AnnouncementViewSet.list` method.
    """
    user = user_with_permissions([("communication", "announcement")])
    prop = property_factory(id=300)
    unit = unit_factory(id=100)

    instance_1 = announcement_factory(
        title="Fly toward heavy great work.",
        properties=(prop,),
        expiry_date=timezone.now() + timedelta(days=1),
        subscription=user.associated_subscription,
    )
    instance_2 = announcement_factory(
        title="Toward.",
        body="Edge husband seek better. Enter yeah huge.",
        expiry_date=timezone.now() - timedelta(days=1),
        subscription=user.associated_subscription,
        units=(unit,),
    )
    instance_3 = announcement_factory(
        title="Himself.",
        properties=(prop,),
        expiry_date=timezone.now() - timedelta(days=2),
        subscription=user.associated_subscription,
    )
    announcement_factory()
    announcements = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("communication:announcement-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = AnnouncementViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [announcements[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count, prop_count, unit_count",
    (
        (
            {},
            {
                "title": ["This field is required."],
                "body": ["This field is required."],
                "send_by_email": ["This field is required."],
                "display_on_tenant_portal": ["This field is required."],
                "display_date": ["This field is required."],
                "expiry_date": ["This field is required."],
            },
            400,
            2,
            0,
            0,
            0,
        ),
        (
            {
                "title": "Lorem",
                "body": "Lorem ipsum dolor",
                "selection": "SPSU",
                "send_by_email": True,
                "display_on_tenant_portal": True,
                "display_date": "2023-09-06",
                "expiry_date": "2023-09-06",
                "properties": [100],
                "units": [100],
            },
            None,
            201,
            11,
            1,
            1,
            1,
        ),
        (
            {
                "title": "Lorem",
                "body": "Lorem ipsum dolor",
                "selection": "APAU",
                "send_by_email": True,
                "display_on_tenant_portal": True,
                "display_date": "2023-09-06",
                "expiry_date": "2023-09-06",
            },
            None,
            201,
            9,
            1,
            2,
            2,
        ),
        (
            {
                "title": "Lorem",
                "body": "Lorem ipsum dolor",
                "selection": "SPAU",
                "send_by_email": True,
                "display_on_tenant_portal": True,
                "display_date": "2023-09-06",
                "expiry_date": "2023-09-06",
                "properties": [100],
            },
            None,
            201,
            10,
            1,
            1,
            1,
        ),
        (
            {
                "title": "Lorem",
                "body": "Lorem ipsum dolor",
                "selection": "APSU",
                "send_by_email": True,
                "display_on_tenant_portal": True,
                "display_date": "2023-09-06",
                "expiry_date": "2023-09-06",
                "units": [200],
            },
            None,
            201,
            10,
            1,
            2,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_announcement_create(
    api_rf,
    user_with_permissions,
    property_factory,
    unit_type_factory,
    unit_factory,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
    prop_count,
    unit_count,
):
    """
    Testing :py:meth:`communication.views.AnnouncementViewSet.create` method.
    """

    user = user_with_permissions([("communication", "announcement")])
    prop_1 = property_factory(id=100)
    prop_2 = property_factory(id=200)
    unit_type_1 = unit_type_factory(parent_property=prop_1)
    unit_type_2 = unit_type_factory(parent_property=prop_2)
    unit_factory(id=100, unit_type=unit_type_1)
    unit_factory(id=200, unit_type=unit_type_2)

    with assertNumQueries(num_queries):
        url = reverse("communication:announcement-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = AnnouncementViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert Announcement.objects.count() == obj_count
    if obj_count > 0:
        announcement = Announcement.objects.first()
        assert announcement.properties.count() == prop_count
        assert announcement.units.count() == unit_count


@pytest.mark.django_db
def test_announcement_retrieve(api_rf, announcement_factory, user_with_permissions):
    """
    Testing :py:meth:`communication.views.AnnouncementViewSet.retrieve` method.
    """

    user = user_with_permissions([("communication", "announcement")])
    announcement = announcement_factory(subscription=user.associated_subscription)

    with assertNumQueries(5):
        url = reverse("communication:announcement-detail", kwargs={"pk": announcement.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = AnnouncementViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=announcement.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "title",
        "body",
        "selection",
        "send_by_email",
        "display_on_tenant_portal",
        "display_date",
        "expiry_date",
        "properties",
        "units",
        "created_at",
        "status",
    }


@pytest.mark.django_db
def test_announcement_update(
    api_rf,
    announcement_factory,
    user_with_permissions,
    property_factory,
    unit_type_factory,
    unit_factory,
):
    """
    Testing :py:meth:`communication.views.AnnouncementViewSet.partial_update` method.
    """

    user = user_with_permissions([("communication", "announcement")])
    announcement = announcement_factory(subscription=user.associated_subscription)
    prop = property_factory()
    unit_type = unit_type_factory(parent_property=prop)
    unit = unit_factory(unit_type=unit_type)

    data = {
        "title": "Lorem",
        "body": "Lorem ipsum dolor",
        "send_by_email": True,
        "display_on_tenant_portal": True,
        "display_date": "2023-09-06",
        "expiry_date": "2023-09-06",
        "properties": [prop.id],
        "units": [unit.id],
    }

    with assertNumQueries(14):
        url = reverse("communication:announcement-detail", kwargs={"pk": announcement.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = AnnouncementViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=announcement.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_announcement_delete(api_rf, announcement_factory, user_with_permissions):
    """
    Testing :py:meth:`communication.views.AnnouncementViewSet.delete` method.
    """

    user = user_with_permissions([("communication", "announcement")])
    announcement = announcement_factory(subscription=user.associated_subscription)

    with assertNumQueries(9):
        url = reverse("communication:announcement-detail", kwargs={"pk": announcement.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = AnnouncementViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=announcement.id)

    assert response.status_code == 204

    assert Announcement.objects.count() == 0


@pytest.mark.django_db
def test_announcement_unit_list(
    api_rf,
    user_with_permissions,
    announcement_factory,
    property_factory,
    unit_type_factory,
    unit_factory,
):
    """
    Testing :py:meth:`communication.views.AnnouncementUnitsListAPIView` view.
    """
    user = user_with_permissions([("property", "unit")])
    prop = property_factory()
    unit_type = unit_type_factory(parent_property=prop)
    unit_1 = unit_factory(unit_type=unit_type, subscription=user.associated_subscription)
    unit_2 = unit_factory(unit_type=unit_type, subscription=user.associated_subscription)
    announcement = announcement_factory(units=(unit_1, unit_2), subscription=user.associated_subscription)

    units = [unit_1.id, unit_2.id]
    index_result = [1, 0]

    with assertNumQueries(19):
        url = reverse(
            "communication:announcement-units-list",
            kwargs={"announcement_id": announcement.id, "property_id": prop.id},
        )
        request = api_rf.get(url, {}, format="json")
        request.user = user
        view = AnnouncementUnitsListAPIView.as_view()
        response = view(request, announcement_id=announcement.id, property_id=prop.id)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [units[i] for i in index_result]
