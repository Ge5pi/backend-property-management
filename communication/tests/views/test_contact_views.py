import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from communication.models import Contact
from communication.views import ContactViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 6),
        ({"search": "john"}, [0], 4),
        ({"search": "paul"}, [1], 4),
        ({"search": "5995"}, [2], 4),
    ),
)
@pytest.mark.django_db
def test_contact_list(api_rf, user_with_permissions, contact_factory, query_params, index_result, num_queries):
    """
    Testing :py:meth:`communication.views.ContactViewSet.list` method.
    """
    user = user_with_permissions([("communication", "contact")])

    instance_1 = contact_factory(
        name="John",
        email="john@example.com",
        primary_contact="+1-773-675-9351",
        subscription=user.associated_subscription,
    )
    instance_2 = contact_factory(
        name="Paul",
        email="paul@example.com",
        primary_contact="+1-196-583-5964",
        subscription=user.associated_subscription,
    )
    instance_3 = contact_factory(
        name="Jsmith",
        email="jsmith@example.com",
        primary_contact="+1-196-583-5995",
        subscription=user.associated_subscription,
    )
    contact_factory()

    contacts = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("communication:contact-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = ContactViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [contacts[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "category": ["This field is required."],
                "primary_contact": ["This field is required."],
                "display_to_tenants": ["This field is required."],
                "selective": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "name": "Douglas Robinson",
                "category": 100,
                "primary_contact": "+19457028805",
                "secondary_contact": "+19457028804",
                "email": "pauldean@example.net",
                "website": "http://www.delacruz.org/",
                "street_address": "844 Dana Village Suite 122",
                "display_to_tenants": True,
                "selective": True,
            },
            None,
            201,
            4,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_contact_create(
    api_rf,
    user_with_permissions,
    contact_category_factory,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`communication.views.ContactViewSet.create` method.
    """

    user = user_with_permissions([("communication", "contact")])
    contact_category_factory(id=100)

    with assertNumQueries(num_queries):
        url = reverse("communication:contact-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = ContactViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert Contact.objects.count() == obj_count


@pytest.mark.django_db
def test_contact_retrieve(api_rf, contact_factory, user_with_permissions):
    """
    Testing :py:meth:`communication.views.ContactViewSet.retrieve` method.
    """

    user = user_with_permissions([("communication", "contact")])
    contact = contact_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse("communication:contact-detail", kwargs={"pk": contact.id})
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


@pytest.mark.django_db
def test_contact_update(api_rf, contact_factory, contact_category_factory, user_with_permissions):
    """
    Testing :py:meth:`communication.views.ContactViewSet.partial_update` method.
    """

    user = user_with_permissions([("communication", "contact")])
    contact_category = contact_category_factory()
    contact = contact_factory(subscription=user.associated_subscription)
    data = {
        "name": "Douglas Robinson",
        "category": contact_category.id,
        "primary_contact": "+19457028805",
        "secondary_contact": "+19457028804",
        "email": "pauldean@example.net",
        "website": "http://www.delacruz.org/",
        "street_address": "844 Dana Village Suite 122",
        "display_to_tenants": True,
        "selective": True,
    }

    with assertNumQueries(5):
        url = reverse("communication:contact-detail", kwargs={"pk": contact.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = ContactViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=contact.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_contact_delete(api_rf, contact_factory, user_with_permissions):
    """
    Testing :py:meth:`communication.views.ContactViewSet.delete` method.
    """

    user = user_with_permissions([("communication", "contact")])
    contact = contact_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse("communication:contact-detail", kwargs={"pk": contact.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = ContactViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=contact.id)

    assert response.status_code == 204

    assert Contact.objects.count() == 0
