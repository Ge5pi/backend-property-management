import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from people.views import TenantViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 12),
        ({"search": "Kathryn"}, [0], 6),
        ({"search": "Brian"}, [1], 6),
        ({"search": "rose@example.com"}, [2], 6),
        ({"status": "Current"}, [2, 1], 9),
        ({"status": "Past"}, [0], 6),
        ({"unit_id": [0]}, [0], 6),
        ({"unit_id": [1]}, [1], 6),
        ({"property_id": [0]}, [0], 6),
        ({"ordering": "pk"}, [0, 1, 2], 12),
        ({"ordering": "-pk"}, [2, 1, 0], 12),
        ({"ordering": "first_name"}, [0, 1, 2], 12),
        ({"ordering": "-first_name"}, [2, 1, 0], 12),
        ({"ordering": "last_name"}, [0, 1, 2], 12),
        ({"ordering": "-last_name"}, [2, 1, 0], 12),
        ({"ordering": "phone_number"}, [0, 1, 2], 12),
        ({"ordering": "-phone_number"}, [2, 1, 0], 12),
    ),
)
@pytest.mark.django_db
def test_tenant_list(
    api_rf,
    user_with_permissions,
    lease_factory,
    applicant_factory,
    rental_application_factory,
    query_params,
    index_result,
    num_queries,
):
    """
    Testing :py:meth:`people.views.TenantViewSet.list` method.
    """
    user = user_with_permissions([("people", "tenant")])

    applicant_1 = applicant_factory(
        first_name="Kathryn",
        last_name="Ball",
        email="john@example.com",
        phone_number="+92311123441",
    )
    applicant_2 = applicant_factory(
        first_name="Kevin",
        last_name="Brian",
        email="brian@example.com",
        phone_number="+92311123442",
    )
    applicant_3 = applicant_factory(
        first_name="Robert",
        last_name="Rose",
        email="rose@example.com",
        phone_number="+92311123443",
    )
    rent_application_1 = rental_application_factory(applicant=applicant_1)
    rent_application_2 = rental_application_factory(applicant=applicant_2)
    rent_application_3 = rental_application_factory(applicant=applicant_3)

    lease_1 = lease_factory(
        rental_application=rent_application_1, status="CLOSED", subscription=user.associated_subscription
    )
    lease_2 = lease_factory(
        rental_application=rent_application_2, status="ACTIVE", subscription=user.associated_subscription
    )
    lease_3 = lease_factory(
        rental_application=rent_application_3, status="ACTIVE", subscription=user.associated_subscription
    )
    lease_factory()

    tenants = [lease_1.primary_tenant.id, lease_2.primary_tenant.id, lease_3.primary_tenant.id]
    units = [lease_1.unit.id, lease_2.unit.id, lease_3.unit.id]
    property_ids = [lease_1.unit.parent_property.id, lease_2.unit.parent_property.id, lease_3.unit.parent_property.id]

    with assertNumQueries(num_queries):
        if "unit_id" in query_params:
            query_params["unit_id"] = [units[i] for i in query_params["unit_id"]]
        if "property_id" in query_params:
            query_params["property_id"] = [property_ids[i] for i in query_params["property_id"]]

        url = reverse("people:tenant-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = TenantViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [tenants[i] for i in index_result]


@pytest.mark.django_db
def test_tenant_retrieve(api_rf, lease_factory, user_with_permissions):
    """
    Testing :py:meth:`people.views.TenantViewSet.retrieve` method.
    """

    user = user_with_permissions([("people", "tenant")])
    tenant = lease_factory(subscription=user.associated_subscription)

    with assertNumQueries(6):
        url = reverse("people:tenant-detail", kwargs={"pk": tenant.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = TenantViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=tenant.id)

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
