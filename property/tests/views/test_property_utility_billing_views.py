import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from property.models import PropertyUtilityBilling
from property.views import PropertyUtilityBillingViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 6),
        ({"parent_property": True}, [2, 1], 6),
    ),
)
@pytest.mark.django_db
def test_property_utility_billing_list(
    api_rf,
    user_with_permissions,
    property_utility_billing_factory,
    query_params,
    index_result,
    num_queries,
    property_factory,
):
    """
    Testing :py:meth:`property.views.PropertyUtilityBillingViewSet.list` method.
    """
    user = user_with_permissions([("property", "propertyutilitybilling")])
    parent_property = property_factory(subscription=user.associated_subscription)

    if query_params.get("parent_property"):
        query_params["parent_property"] = parent_property.id

    property_utility_billing_1 = property_utility_billing_factory(subscription=user.associated_subscription)
    property_utility_billing_2 = property_utility_billing_factory(
        parent_property=parent_property, subscription=user.associated_subscription
    )
    property_utility_billing_3 = property_utility_billing_factory(
        parent_property=parent_property, subscription=user.associated_subscription
    )
    property_utility_billing_factory()

    property_upcoming_activities = [
        property_utility_billing_1.id,
        property_utility_billing_2.id,
        property_utility_billing_3.id,
    ]

    with assertNumQueries(num_queries):
        url = reverse("property:property_utility_billing-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = PropertyUtilityBillingViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [property_upcoming_activities[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "utility": ["This field is required."],
                "vendor": ["This field is required."],
                "vendor_bill_gl": ["This field is required."],
                "tenant_charge_gl": ["This field is required."],
                "owner_contribution_percentage": ["This field is required."],
                "tenant_contribution_percentage": ["This field is required."],
                "parent_property": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "utility": "Electricity",
                "vendor_bill_gl": "123",
                "tenant_charge_gl": "456",
                "owner_contribution_percentage": 10,
                "tenant_contribution_percentage": 90,
            },
            None,
            201,
            5,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_property_utility_billing_create(
    api_rf,
    property_factory,
    vendor_factory,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`property.views.PropertyUtilityBillingViewSet.create` method.
    """

    user = user_with_permissions([("property", "propertyutilitybilling")])

    if status_code == 201:
        data["parent_property"] = property_factory().id
        data["vendor"] = vendor_factory().id

    with assertNumQueries(num_queries):
        url = reverse("property:property_utility_billing-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = PropertyUtilityBillingViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert PropertyUtilityBilling.objects.count() == obj_count


@pytest.mark.django_db
def test_property_utility_billing_retrieve(api_rf, property_utility_billing_factory, user_with_permissions):
    """
    Testing :py:meth:`property.views.PropertyUtilityBillingViewSet.retrieve` method.
    """

    user = user_with_permissions([("property", "propertyutilitybilling")])
    property_utility_billing = property_utility_billing_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse("property:property_utility_billing-detail", kwargs={"pk": property_utility_billing.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = PropertyUtilityBillingViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=property_utility_billing.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "utility",
        "vendor",
        "vendor_bill_gl",
        "tenant_charge_gl",
        "owner_contribution_percentage",
        "tenant_contribution_percentage",
        "parent_property",
        "vendor_full_name",
    }


@pytest.mark.django_db
def test_property_utility_billing_update(api_rf, property_utility_billing_factory, user_with_permissions):
    """
    Testing :py:meth:`property.views.PropertyUtilityBillingViewSet.partial_update` method.
    """

    user = user_with_permissions([("property", "propertyutilitybilling")])
    property_utility_billing = property_utility_billing_factory(subscription=user.associated_subscription)
    data = {
        "utility": "Electricity",
        "vendor": property_utility_billing.vendor.id,
        "vendor_bill_gl": "123",
        "tenant_charge_gl": "456",
        "owner_contribution_percentage": 10,
        "tenant_contribution_percentage": 90,
        "parent_property": property_utility_billing.parent_property.id,
    }

    with assertNumQueries(6):
        url = reverse("property:property_utility_billing-detail", kwargs={"pk": property_utility_billing.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = PropertyUtilityBillingViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=property_utility_billing.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_property_utility_billing_delete(api_rf, property_utility_billing_factory, user_with_permissions):
    """
    Testing :py:meth:`property.views.PropertyUtilityBillingViewSet.delete` method.
    """

    user = user_with_permissions([("property", "propertyutilitybilling")])
    property_utility_billing = property_utility_billing_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse(
            "property:property_utility_billing-detail",
            kwargs={"pk": property_utility_billing.id},
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = PropertyUtilityBillingViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=property_utility_billing.id)

    assert response.status_code == 204

    assert PropertyUtilityBilling.objects.count() == 0
