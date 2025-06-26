import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from property.models import PropertyOwner
from property.views import PropertyOwnerViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"parent_property": 1}, [1, 0], 4),
    ),
)
@pytest.mark.django_db
def test_property_owner_list(
    api_rf,
    query_params,
    index_result,
    num_queries,
    user_with_permissions,
    property_owner_factory,
    property_factory,
):
    """
    Testing :py:meth:`property.views.PropertyOwnerListAPIView` method.
    """
    user = user_with_permissions([("property", "propertyowner")])
    prop = property_factory(subscription=user.associated_subscription)

    if "parent_property" in query_params:
        query_params["parent_property"] = prop.id

    instance_1 = property_owner_factory(parent_property=prop, subscription=user.associated_subscription)
    instance_2 = property_owner_factory(parent_property=prop, subscription=user.associated_subscription)
    instance_3 = property_owner_factory(subscription=user.associated_subscription)
    property_owner_factory()

    property_owners = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("property:property_owners-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = PropertyOwnerViewSet.as_view({"get": "list"})
        response = view(request, property_id=prop.id)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [property_owners[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "owner": ["This field is required."],
                "percentage_owned": ["This field is required."],
                "parent_property": ["This field is required."],
                "payment_type": ["This field is required."],
                "reserve_funds": ["This field is required."],
                "contract_expiry": ["This field is required."],
                "fiscal_year_end": ["This field is required."],
                "ownership_start_date": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "percentage_owned": 50,
                "payment_type": "net_income",
                "reserve_funds": "1000.00",
                "contract_expiry": "2020-12-31",
                "fiscal_year_end": "2020-12-31",
                "ownership_start_date": "2020-01-01",
            },
            None,
            201,
            6,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_property_owner_create(
    api_rf,
    property_factory,
    owner_people_factory,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`property.views.PropertyOwnerViewSet.create` method.
    """

    user = user_with_permissions([("property", "propertyowner")])

    if status_code == 201:
        data["parent_property"] = property_factory().id
        data["owner"] = owner_people_factory().id

    with assertNumQueries(num_queries):
        url = reverse("property:property_owners-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = PropertyOwnerViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert PropertyOwner.objects.count() == obj_count


@pytest.mark.django_db
def test_property_owner_retrieve(api_rf, property_owner_factory, user_with_permissions):
    """
    Testing :py:meth:`property.views.PropertyOwnerViewSet.retrieve` method.
    """

    user = user_with_permissions([("property", "propertyowner")])
    property_owner = property_owner_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse(
            "property:property_owners-detail",
            kwargs={"pk": property_owner.id},
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = PropertyOwnerViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=property_owner.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "first_name",
        "last_name",
        "owner",
        "percentage_owned",
        "parent_property",
        "payment_type",
        "get_payment_type_display",
        "reserve_funds",
        "contract_expiry",
        "fiscal_year_end",
        "ownership_start_date",
    }


@pytest.mark.django_db
def test_property_owner_update(api_rf, property_owner_factory, user_with_permissions, property_factory):
    """
    Testing :py:meth:`property.views.PropertyOwnerViewSet.partial_update` method.
    """

    user = user_with_permissions([("property", "propertyowner")])
    property_owner = property_owner_factory(subscription=user.associated_subscription)
    data = {
        "percentage_owned": 50,
        "payment_type": "net_income",
        "reserve_funds": "1000.00",
        "contract_expiry": "2020-12-31",
        "fiscal_year_end": "2020-12-31",
        "ownership_start_date": "2020-01-01",
    }

    with assertNumQueries(6):
        url = reverse(
            "property:property_owners-detail",
            kwargs={"pk": property_owner.id},
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = PropertyOwnerViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=property_owner.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_property_owner_delete(api_rf, property_owner_factory, user_with_permissions):
    """
    Testing :py:meth:`property.views.PropertyOwnerViewSet.delete` method.
    """

    user = user_with_permissions([("property", "propertyowner")])
    property_owner = property_owner_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse(
            "property:property_owners-detail",
            kwargs={"pk": property_owner.id},
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = PropertyOwnerViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=property_owner.id)

    assert response.status_code == 204

    assert PropertyOwner.objects.count() == 0
