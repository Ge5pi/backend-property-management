import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from tenant.views import TenantRetrieveAPIView


@pytest.mark.django_db
def test_tenant_retrieve(api_rf, tenant_user_with_permissions):
    """
    Testing :py:meth:`tenant.views.TenantRetrieveAPIView.retrieve` method.
    """

    user, _ = tenant_user_with_permissions([("people", "tenant")])

    with assertNumQueries(9):
        url = reverse("tenant:tenant-retrieve")
        request = api_rf.get(url, format="json")
        request.user = user
        view = TenantRetrieveAPIView.as_view()
        response = view(request)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "status",
        "property_name",
        "unit_name",
        "lease",
        "address",
        "property_id",
        "unit_id",
        "rental_application_id",
    }
