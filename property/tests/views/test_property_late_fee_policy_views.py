import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from property.views import PropertyLateFeePolicyViewSet


@pytest.mark.django_db
def test_property_late_fee_policy_retrieve(api_rf, property_factory, user_with_permissions):
    """
    Testing :py:meth:`property.views.PropertyLateFeePolicyViewSet.retrieve` method.
    """

    user = user_with_permissions([("property", "propertylatefeepolicy")])
    prop = property_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse("property:property_late_fee_policy-detail", kwargs={"pk": prop.late_fee_policy.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = PropertyLateFeePolicyViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=prop.late_fee_policy.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "start_date",
        "end_date",
        "late_fee_type",
        "get_late_fee_type_display",
        "base_amount_fee",
        "eligible_charges",
        "get_eligible_charges_display",
        "charge_daily_late_fees",
        "daily_amount_per_month_max",
        "grace_period_type",
        "grace_period",
    }


@pytest.mark.django_db
def test_property_late_fee_policy_update(api_rf, property_factory, user_with_permissions):
    """
    Testing :py:meth:`property.views.PropertyLateFeePolicyViewSet.partial_update` method.
    """

    user = user_with_permissions([("property", "propertylatefeepolicy")])
    prop = property_factory(subscription=user.associated_subscription)
    data = {
        "start_date": "2020-01-01",
        "end_date": "2020-12-31",
        "late_fee_type": "flat",
        "base_amount_fee": "100.00",
        "eligible_charges": "every_charge",
        "charge_daily_late_fees": True,
        "daily_amount_per_month_max": "100.00",
        "grace_period_type": "no_grace_period",
        "grace_period": 5,
    }

    with assertNumQueries(4):
        url = reverse("property:property_late_fee_policy-detail", kwargs={"pk": prop.late_fee_policy.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = PropertyLateFeePolicyViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=prop.late_fee_policy.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value
