import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from maintenance.models import ServiceRequest
from tenant.views import ServiceRequestViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 17),
        ({"search": "srq-1"}, [0], 15),
        ({"search": "success thus yourself treatment"}, [1], 15),
        ({"search": "newspaper matter score wide"}, [0], 15),
        ({"ordering": "description"}, [0, 1, 2], 17),
        ({"ordering": "-description"}, [2, 1, 0], 17),
        ({"ordering": "subject"}, [0, 2, 1], 17),
        ({"ordering": "-subject"}, [1, 2, 0], 17),
        ({"priority": "URGENT"}, [1], 15),
        ({"order_type": "RESIDENT"}, [2], 15),
        ({"work_order_status": "OPEN"}, [2], 15),
        ({"status": "COMPLETED"}, [1], 15),
    ),
)
@pytest.mark.django_db
def test_service_request_list(
    api_rf,
    tenant_user_with_permissions,
    service_request_factory,
    query_params,
    index_result,
    num_queries,
    work_order_factory,
):
    """
    Testing :py:meth:`tenant.views.ServiceRequestViewSet.list` method.
    """
    user, lease = tenant_user_with_permissions([("maintenance", "servicerequest")])

    instance_1 = service_request_factory(
        subject="Case newspaper matter score wide both in.",
        description="Course charge system they.",
        unit=lease.unit,
        order_type="INTERNAL",
        subscription=user.associated_subscription,
    )
    instance_2 = service_request_factory(
        subject="Must line air theory name.",
        description="Short success thus yourself treatment condition often.",
        unit=lease.unit,
        priority="URGENT",
        order_type="INTERNAL",
        subscription=user.associated_subscription,
    )
    instance_3 = service_request_factory(
        subject="Either own agree fast public manage.",
        description="Thus traditional know wonder.",
        unit=lease.unit,
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
        url = reverse("tenant:service_requests-list")
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
            9,
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
            12,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_service_request_create(
    api_rf, tenant_user_with_permissions, unit_factory, data, expected_response, status_code, num_queries, obj_count
):
    """
    Testing :py:meth:`tenant.views.ServiceRequestViewSet.create` method.
    """
    user, lease = tenant_user_with_permissions([("maintenance", "servicerequest")], id=100)
    unit = lease.unit

    if status_code == 201:
        data["unit"] = unit.id

    with assertNumQueries(num_queries):
        url = reverse("tenant:service_requests-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = ServiceRequestViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert ServiceRequest.objects.count() == obj_count


@pytest.mark.django_db
def test_service_request_retrieve(api_rf, service_request_factory, tenant_user_with_permissions):
    """
    Testing :py:meth:`tenant.views.ServiceRequestViewSet.retrieve` method.
    """
    user, lease = tenant_user_with_permissions([("maintenance", "servicerequest")])
    service_request = service_request_factory(subscription=user.associated_subscription, unit=lease.unit)

    with assertNumQueries(15):
        url = reverse("tenant:service_requests-detail", kwargs={"pk": service_request.id})
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
def test_service_request_update(api_rf, tenant_user_with_permissions, service_request_factory):
    """
    Testing :py:meth:`tenant.views.ServiceRequestViewSet.update` method.
    """
    user, lease = tenant_user_with_permissions([("maintenance", "servicerequest")], id=100)
    service_request = service_request_factory(subscription=user.associated_subscription, unit=lease.unit)

    data = {
        "unit": service_request.unit.id,
        "subject": "Course charge system they.",
        "order_type": "RESIDENT",
        "permission_to_enter": True,
        "additional_information_for_entry": "Read line shake short term.",
        "priority": "LOW",
        "description": "Read line shake short term.",
    }

    with assertNumQueries(17):
        url = reverse("tenant:service_requests-detail", kwargs={"pk": service_request.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = ServiceRequestViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=service_request.id)

    assert response.status_code == 200

    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_service_request_delete(api_rf, service_request_factory, tenant_user_with_permissions):
    """
    Testing :py:meth:`tenant.views.ServiceRequestViewSet.delete` method.
    """
    user, lease = tenant_user_with_permissions([("maintenance", "servicerequest")])
    service_request = service_request_factory(subscription=user.associated_subscription, unit=lease.unit)

    with assertNumQueries(17):
        url = reverse("tenant:service_requests-detail", kwargs={"pk": service_request.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = ServiceRequestViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=service_request.id)
    assert response.status_code == 204
    assert ServiceRequest.objects.count() == 0
