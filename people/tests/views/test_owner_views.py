import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from people.models import Owner
from people.views import OwnerOwnedPropertiesListAPIView, OwnerViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"search": "Michael"}, [0], 3),
        ({"search": "Lawrence"}, [1], 3),
        ({"search": "Wright-Brennan"}, [2], 3),
        ({"ordering": "pk"}, [0, 1, 2], 3),
        ({"ordering": "-pk"}, [2, 1, 0], 3),
        ({"ordering": "first_name"}, [2, 1, 0], 3),
        ({"ordering": "-first_name"}, [0, 1, 2], 3),
        ({"ordering": "last_name"}, [2, 1, 0], 3),
        ({"ordering": "-last_name"}, [0, 1, 2], 3),
        ({"ordering": "company_name"}, [1, 0, 2], 3),
        ({"ordering": "-company_name"}, [2, 0, 1], 3),
    ),
)
@pytest.mark.django_db
def test_owner_list(
    api_rf,
    user_with_permissions,
    owner_people_factory,
    query_params,
    index_result,
    num_queries,
):
    """
    Testing :py:meth:`people.views.OwnerViewSet.list` method.
    """
    user = user_with_permissions([("people", "owner")])
    owner_1 = owner_people_factory(
        first_name="Michael",
        last_name="Rhodes",
        company_name="Stokes-Forbes",
        subscription=user.associated_subscription,
    )
    owner_2 = owner_people_factory(
        first_name="John", last_name="Lawrence", company_name="Meyer Inc", subscription=user.associated_subscription
    )
    owner_3 = owner_people_factory(
        first_name="Alex", last_name="Chan", company_name="Wright-Brennan", subscription=user.associated_subscription
    )
    owner_people_factory()

    owners = [
        owner_1.id,
        owner_2.id,
        owner_3.id,
    ]

    with assertNumQueries(num_queries):
        url = reverse("people:owner_people-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = OwnerViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [owners[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "first_name": ["This field is required."],
                "last_name": ["This field is required."],
                "personal_contact_numbers": ["This field is required."],
                "company_contact_numbers": ["This field is required."],
                "personal_emails": ["This field is required."],
                "company_emails": ["This field is required."],
                "tax_payer": ["This field is required."],
                "tax_payer_id": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "first_name": "Kevin",
                "last_name": "Jones",
                "company_name": "back",
                "personal_contact_numbers": ["+923111234455"],
                "company_contact_numbers": ["+923111234455"],
                "personal_emails": ["jamesandrea@example.com"],
                "company_emails": ["gabrielaspears@example.com"],
                "street_address": "561 Mosley Camp",
                "city": "New Jack",
                "state": "Connecticut",
                "zip": "74424",
                "country": "Botswana",
                "tax_payer": "Stephanie",
                "tax_payer_id": "255",
                "bank_account_title": "Hannah",
                "bank_name": "assume",
                "bank_branch": "North Mary",
                "bank_routing_number": "193",
                "bank_account_number": "653",
                "notes": "During star effort get such. Final find cost enter machine rate.",
                "is_company_name_as_tax_payer": True,
                "is_use_as_display_name": False,
            },
            None,
            201,
            3,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_owner_create(
    api_rf,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`people.views.OwnerViewSet.create` method.
    """

    user = user_with_permissions([("people", "owner")])

    with assertNumQueries(num_queries):
        url = reverse("people:owner_people-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = OwnerViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert Owner.objects.count() == obj_count


@pytest.mark.django_db
def test_owner_retrieve(api_rf, owner_people_factory, user_with_permissions):
    """
    Testing :py:meth:`people.views.OwnerViewSet.retrieve` method.
    """

    user = user_with_permissions([("people", "owner")])
    owner = owner_people_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse("people:owner_people-detail", kwargs={"pk": owner.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = OwnerViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=owner.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "first_name",
        "last_name",
        "company_name",
        "personal_contact_numbers",
        "company_contact_numbers",
        "personal_emails",
        "company_emails",
        "street_address",
        "city",
        "state",
        "zip",
        "country",
        "tax_payer",
        "tax_payer_id",
        "bank_account_title",
        "bank_name",
        "bank_branch",
        "bank_routing_number",
        "bank_account_number",
        "notes",
        "is_company_name_as_tax_payer",
        "is_use_as_display_name",
    }


@pytest.mark.django_db
def test_owner_update(api_rf, owner_people_factory, user_with_permissions):
    """
    Testing :py:meth:`people.views.OwnerViewSet.partial_update` method.
    """

    user = user_with_permissions([("people", "owner")])
    owner = owner_people_factory(subscription=user.associated_subscription)
    data = {
        "first_name": "Kevin",
        "last_name": "Jones",
        "company_name": "back",
        "personal_contact_numbers": ["+923111234455"],
        "company_contact_numbers": ["+923111234455"],
        "personal_emails": ["jamesandrea@example.com"],
        "company_emails": ["gabrielaspears@example.com"],
        "street_address": "561 Mosley Camp",
        "city": "New Jack",
        "state": "Connecticut",
        "zip": "74424",
        "country": "Botswana",
        "tax_payer": "Stephanie",
        "tax_payer_id": "255",
        "bank_account_title": "Hannah",
        "bank_name": "assume",
        "bank_branch": "North Mary",
        "bank_routing_number": "193",
        "bank_account_number": "653",
        "notes": "During star effort get such. Final find cost enter machine rate.",
        "is_company_name_as_tax_payer": True,
        "is_use_as_display_name": False,
    }

    with assertNumQueries(4):
        url = reverse("people:owner_people-detail", kwargs={"pk": owner.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = OwnerViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=owner.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_owner_delete(api_rf, owner_people_factory, user_with_permissions):
    """
    Testing :py:meth:`people.views.OwnerViewSet.delete` method.
    """

    user = user_with_permissions([("people", "owner")])
    owner = owner_people_factory(subscription=user.associated_subscription)

    with assertNumQueries(8):
        url = reverse("people:owner_people-detail", kwargs={"pk": owner.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = OwnerViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=owner.id)

    assert response.status_code == 204

    assert Owner.objects.count() == 0


@pytest.mark.django_db
def test_owner_owned_properties_list(
    api_rf, user_with_permissions, owner_people_factory, property_owner_factory, property_factory
):
    """
    Testing :py:meth:`people.views.OwnerOwnedPropertiesListAPIView.list` method.
    """
    user = user_with_permissions([("property", "propertyowner")])

    parent_property = property_factory(subscription=user.associated_subscription)
    owner_people = owner_people_factory(subscription=user.associated_subscription)
    owner = property_owner_factory(
        parent_property=parent_property, owner=owner_people, subscription=user.associated_subscription
    )

    properties = [owner.id]
    index_result = [0]

    with assertNumQueries(3):
        url = reverse("people:owner-owned-properties", kwargs={"owner_id": owner_people.id})
        request = api_rf.get(url, {}, format="json")
        request.user = user
        view = OwnerOwnedPropertiesListAPIView.as_view()
        response = view(request, owner_id=owner_people.id)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [properties[i] for i in index_result]
