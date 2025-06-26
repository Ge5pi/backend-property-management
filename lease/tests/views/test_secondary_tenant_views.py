import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from lease.models import SecondaryTenant
from lease.views import SecondaryTenantViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (({}, [2, 1, 0], 3), ({"lease": 0}, [0], 4)),
)
@pytest.mark.django_db
def test_secondary_tenant_list(
    api_rf, user_with_permissions, secondary_tenant_factory, query_params, index_result, num_queries, lease_factory
):
    """
    Testing :py:meth:`lease.views.SecondaryTenantViewSet.list` method.
    """
    user = user_with_permissions([("lease", "secondarytenant")])
    lease = lease_factory()
    leases = [lease.id]

    if "lease" in query_params:
        query_params["lease"] = leases[query_params["lease"]]

    instance_1 = secondary_tenant_factory(lease=lease, subscription=user.associated_subscription)
    instance_2 = secondary_tenant_factory(subscription=user.associated_subscription)
    instance_3 = secondary_tenant_factory(subscription=user.associated_subscription)
    secondary_tenant_factory()

    secondary_tenants = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("lease:secondary-tenant-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = SecondaryTenantViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [secondary_tenants[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "first_name": ["This field is required."],
                "last_name": ["This field is required."],
                "birthday": ["This field is required."],
                "phone_number": ["This field is required."],
                "tax_payer_id": ["This field is required."],
                "lease": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "birthday": "2021-01-01",
                "phone_number": "+923111234455",
                "tax_payer_id": "123456789",
                "description": "Test Description",
            },
            None,
            201,
            4,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_secondary_tenant_create(
    api_rf, user_with_permissions, data, expected_response, status_code, num_queries, lease_factory, obj_count
):
    """
    Testing :py:meth:`lease.views.SecondaryTenantViewSet.create` method.
    """
    lease = lease_factory()
    user = user_with_permissions([("lease", "secondarytenant")])

    if status_code == 201:
        data["lease"] = lease.id

    with assertNumQueries(num_queries):
        url = reverse("lease:secondary-tenant-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = SecondaryTenantViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert SecondaryTenant.objects.count() == obj_count


@pytest.mark.django_db
def test_secondary_tenant_retrieve(api_rf, secondary_tenant_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.SecondaryTenantViewSet.retrieve` method.
    """

    user = user_with_permissions([("lease", "secondarytenant")])
    secondary_tenant = secondary_tenant_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse("lease:secondary-tenant-detail", kwargs={"pk": secondary_tenant.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = SecondaryTenantViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=secondary_tenant.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "first_name",
        "last_name",
        "email",
        "birthday",
        "phone_number",
        "tax_payer_id",
        "description",
        "lease",
    }


@pytest.mark.django_db
def test_secondary_tenant_update(api_rf, secondary_tenant_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.SecondaryTenantViewSet.partial_update` method.
    """

    user = user_with_permissions([("lease", "secondarytenant")])
    secondary_tenant = secondary_tenant_factory(subscription=user.associated_subscription)
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "birthday": "2021-01-01",
        "phone_number": "+923111234455",
        "tax_payer_id": "123456789",
        "description": "Test Description",
        "lease": secondary_tenant.lease.id,
    }

    with assertNumQueries(5):
        url = reverse("lease:secondary-tenant-detail", kwargs={"pk": secondary_tenant.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = SecondaryTenantViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=secondary_tenant.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_secondary_tenant_delete(api_rf, secondary_tenant_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.SecondaryTenantViewSet.delete` method.
    """

    user = user_with_permissions([("lease", "secondarytenant")])
    secondary_tenant = secondary_tenant_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse("lease:secondary-tenant-detail", kwargs={"pk": secondary_tenant.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = SecondaryTenantViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=secondary_tenant.id)

    assert response.status_code == 204

    assert SecondaryTenant.objects.count() == 0
