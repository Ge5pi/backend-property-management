import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from tenant.views import ContactViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 9),
        ({"search": "john"}, [0], 7),
        ({"search": "paul"}, [1], 7),
        ({"search": "5995"}, [2], 7),
    ),
)
@pytest.mark.django_db
def test_contact_list(api_rf, tenant_user_with_permissions, contact_factory, query_params, index_result, num_queries):
    """
    Testing :py:meth:`tenant.views.ContactViewSet.list` method.
    """
    user, _ = tenant_user_with_permissions([("communication", "contact")])

    instance_1 = contact_factory(
        name="John",
        email="john@example.com",
        primary_contact="+1-773-675-9351",
        subscription=user.associated_subscription,
        display_to_tenants=True,
    )
    instance_2 = contact_factory(
        name="Paul",
        email="paul@example.com",
        primary_contact="+1-196-583-5964",
        subscription=user.associated_subscription,
        display_to_tenants=True,
    )
    instance_3 = contact_factory(
        name="Jsmith",
        email="jsmith@example.com",
        primary_contact="+1-196-583-5995",
        subscription=user.associated_subscription,
        display_to_tenants=True,
    )
    contact_factory()

    contacts = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("tenant:contact-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = ContactViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [contacts[i] for i in index_result]


@pytest.mark.django_db
def test_contact_retrieve(api_rf, contact_factory, tenant_user_with_permissions):
    """
    Testing :py:meth:`tenant.views.ContactViewSet.retrieve` method.
    """

    user, _ = tenant_user_with_permissions([("communication", "contact")])
    contact = contact_factory(subscription=user.associated_subscription, display_to_tenants=True)

    with assertNumQueries(7):
        url = reverse("tenant:contact-detail", kwargs={"pk": contact.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = ContactViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=contact.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "name",
        "category",
        "category_name",
        "primary_contact",
        "secondary_contact",
        "email",
        "website",
        "street_address",
        "display_to_tenants",
        "selective",
    }
