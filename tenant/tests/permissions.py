import pytest
from django.urls import reverse

from tenant.views import InvoiceViewSet


@pytest.mark.parametrize(
    "lease_status, expected_status_code, expected_response",
    (
        ("ACTIVE", 200, []),
        ("CLOSED", 403, {"detail": "You do not have permission to perform this action."}),
    ),
)
@pytest.mark.django_db
def test_tenant_permission_check_fail(
    api_rf, lease_factory, user_with_permissions, lease_status, expected_status_code, expected_response
):
    """
    Testing that tenant permission check fails when tenant is not provided.
    """
    user = user_with_permissions([("accounting", "invoice")])
    lease = lease_factory(status=lease_status)
    lease.primary_tenant.user = user
    lease.primary_tenant.save()

    url = reverse("system_preferences:business-information-list")
    request = api_rf.get(url, {}, format="json")
    request.user = user
    view = InvoiceViewSet.as_view({"get": "list"})
    response = view(request)

    assert response.status_code == expected_status_code
    assert response.data == expected_response
