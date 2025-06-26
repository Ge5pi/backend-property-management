import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from maintenance.models import ServiceRequest
from maintenance.views import ServiceRequestViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 6),
        ({"search": "srq-1"}, [0], 4),
        ({"search": "success thus yourself treatment"}, [1], 4),
        ({"ordering": "description"}, [0, 1, 2], 6),
        ({"ordering": "-description"}, [2, 1, 0], 6),
        ({"ordering": "unit__parent_property__name"}, [0, 2, 1], 6),
        ({"ordering": "-unit__parent_property__name"}, [1, 2, 0], 6),
        ({"priority": "URGENT"}, [1], 4),
        ({"order_type": "RESIDENT"}, [2], 4),
        ({"work_order_status": "OPEN"}, [2], 4),
        ({"status": "COMPLETED"}, [1], 4),
    ),
)
@pytest.mark.django_db
def test_service_request_list(
    api_rf,
    user_with_permissions,
    service_request_factory,
    query_params,
    index_result,
    num_queries,
    property_factory,
    unit_factory,
    unit_type_factory,
    work_order_factory,
):
    """
    Testing :py:meth:`maintenance.views.ServiceRequestViewSet.list` method.
    """
    user = user_with_permissions([("maintenance", "servicerequest")])

    prop_1 = property_factory(name="Article hard medical include citizen experience")
    unit_type_1 = unit_type_factory(parent_property=prop_1)
    unit_1 = unit_factory(parent_property=prop_1, unit_type=unit_type_1)

    prop_2 = property_factory(name="Really evidence concern")
    unit_type_2 = unit_type_factory(parent_property=prop_2)
    unit_2 = unit_factory(parent_property=prop_2, unit_type=unit_type_2)

    prop_3 = property_factory(name="Eat detail present")
    unit_type_3 = unit_type_factory(parent_property=prop_3)
    unit_3 = unit_factory(parent_property=prop_3, unit_type=unit_type_3)

    instance_1 = service_request_factory(
        description="Course charge system they.",
        unit=unit_1,
        order_type="INTERNAL",
        subscription=user.associated_subscription,
    )
    instance_2 = service_request_factory(
        description="Short success thus yourself treatment condition often.",
        unit=unit_2,
        priority="URGENT",
        order_type="INTERNAL",
        subscription=user.associated_subscription,
    )
    instance_3 = service_request_factory(
        description="Thus traditional know wonder.",
        unit=unit_3,
        order_type="RESIDENT",
        subscription=user.associated_subscription,
    )
    service_request_factory()

    if query_params.get("search") == "srq-1":
        query_params["search"] = f"srq-{instance_1.id}"

    work_order_factory(service_request_id=instance_3.id, status="OPEN", subscription=user.associated_subscription)
    work_order_factory(service_request_id=instance_2.id, status="COMPLETED", subscription=user.associated_subscription)

    service_request_ids = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("maintenance:service_requests-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = ServiceRequestViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [service_request_ids[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "subject": ["This field is required."],
                "unit": ["This field is required."],
                "order_type": ["This field is required."],
                "priority": ["This field is required."],
                "description": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "subject": "Course charge system they.",
                "order_type": "RESIDENT",
                "permission_to_enter": True,
                "additional_information_for_entry": "Read line shake short term.",
                "priority": "LOW",
                "description": "Read line shake short term.",
            },
            None,
            201,
            5,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_service_request_create(
    api_rf, user_with_permissions, unit_factory, data, expected_response, status_code, num_queries, obj_count
):
    """
    Testing :py:meth:`maintenance.views.ServiceRequestViewSet.create` method.
    """
    user = user_with_permissions([("maintenance", "servicerequest")], id=100)
    unit = unit_factory()

    if status_code == 201:
        data["unit"] = unit.id

    with assertNumQueries(num_queries):
        url = reverse("maintenance:service_requests-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = ServiceRequestViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert ServiceRequest.objects.count() == obj_count


@pytest.mark.django_db
def test_service_request_retrieve(api_rf, service_request_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.ServiceRequestViewSet.retrieve` method.
    """
    user = user_with_permissions([("maintenance", "servicerequest")])
    service_request = service_request_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse("maintenance:service_requests-detail", kwargs={"pk": service_request.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = ServiceRequestViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=service_request.id)

    assert response.status_code == 200
    assert response.data.keys() == {
        "id",
        "slug",
        "unit",
        "status",
        "order_type",
        "get_order_type_display",
        "permission_to_enter",
        "additional_information_for_entry",
        "priority",
        "get_priority_display",
        "subject",
        "description",
        "property_id",
        "tenant_id",
        "work_order_count",
        "property_name",
        "unit_name",
        "unit_cover_picture",
        "created_at",
    }


@pytest.mark.django_db
def test_service_request_update(api_rf, user_with_permissions, service_request_factory):
    """
    Testing :py:meth:`maintenance.views.ServiceRequestViewSet.update` method.
    """
    user = user_with_permissions([("maintenance", "servicerequest")], id=100)
    service_request = service_request_factory(subscription=user.associated_subscription)

    data = {
        "unit": service_request.unit.id,
        "subject": "Course charge system they.",
        "order_type": "RESIDENT",
        "permission_to_enter": True,
        "additional_information_for_entry": "Read line shake short term.",
        "priority": "LOW",
        "description": "Read line shake short term.",
    }

    with assertNumQueries(6):
        url = reverse("maintenance:service_requests-detail", kwargs={"pk": service_request.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = ServiceRequestViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=service_request.id)

    assert response.status_code == 200

    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_service_request_delete(api_rf, service_request_factory, user_with_permissions):
    """
    Testing :py:meth:`maintenance.views.ServiceRequestViewSet.delete` method.
    """
    user = user_with_permissions([("maintenance", "servicerequest")])
    service_request = service_request_factory(subscription=user.associated_subscription)

    with assertNumQueries(6):
        url = reverse("maintenance:service_requests-detail", kwargs={"pk": service_request.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = ServiceRequestViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=service_request.id)
    assert response.status_code == 204
    assert ServiceRequest.objects.count() == 0
