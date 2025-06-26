import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from tenant.views import LeaseViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (({}, [0], 16),),
)
@pytest.mark.django_db
def test_lease_list(api_rf, tenant_user_with_permissions, query_params, index_result, num_queries):
    """
    Testing :py:meth:`tenant.views.LeaseViewSet.list` method.
    """
    user, lease = tenant_user_with_permissions([("lease", "lease")])

    leases = [lease.id]

    with assertNumQueries(num_queries):
        url = reverse("tenant:lease-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = LeaseViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [leases[i] for i in index_result]


@pytest.mark.django_db
def test_lease_retrieve(api_rf, tenant_user_with_permissions):
    """
    Testing :py:meth:`tenant.views.LeaseViewSet.retrieve` method.
    """

    user, lease = tenant_user_with_permissions([("lease", "lease")])

    with assertNumQueries(16):
        url = reverse("tenant:lease-detail", kwargs={"pk": lease.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = LeaseViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=lease.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "rental_application",
        "lease_type",
        "get_lease_type_display",
        "start_date",
        "end_date",
        "lease_template",
        "rent_cycle",
        "get_rent_cycle_display",
        "amount",
        "gl_account",
        "description",
        "due_date",
        "status",
        "get_status_display",
        "closed_on",
        "unit",
        "created_at",
        "primary_tenant",
        "property_id",
        "property_name",
        "unit_name",
        "tenant_first_name",
        "tenant_last_name",
        "owners",
        "applicant_id",
    }
