import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from system_preferences.models import ManagementFee
from system_preferences.views import ManagementFeeViewSet


@pytest.mark.parametrize(
    "query_params, index_result",
    (
        ({}, [0, 1, 2]),
        ({"search": "1"}, [0]),
        ({"search": "2"}, [0, 1, 2]),
        ({"search": "4"}, [1, 2]),
        ({"search": "PK-"}, [0, 1, 2]),
        ({"ordering": "created_at"}, [0, 1, 2]),
        ({"ordering": "-created_at"}, [2, 1, 0]),
        ({"status": "ACTIVE"}, [2]),
        ({"status": "INACTIVE"}, [0, 1]),
    ),
)
@pytest.mark.django_db
def test_management_fee_list(
    api_rf, user_with_permissions, management_fee_factory, freezer, query_params, index_result
):
    """
    Testing :py:meth:`system_preferences.views.ManagementFeeViewSet.list` method.
    """
    user = user_with_permissions([("system_preferences", "managementfee")])

    management_fee_factory()
    freezer.move_to("2020-01-01")
    instance_1 = management_fee_factory(
        fee="100", fee_type="fee", gl_account="PK-111-222-333", subscription=user.associated_subscription
    )
    freezer.move_to("2020-01-02")
    instance_2 = management_fee_factory(
        fee="557", fee_type="BY_PERCENTAGE", gl_account="PK-456-789-772", subscription=user.associated_subscription
    )
    freezer.move_to("2020-01-03")
    instance_3 = management_fee_factory(
        fee="735", fee_type="fee", gl_account="PK-323-654-987", subscription=user.associated_subscription
    )

    management_fees = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(3):
        url = reverse("system_preferences:management-fee-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = ManagementFeeViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [management_fees[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {"fee": "100.10", "fee_type": "FLAT_FEE"},
            {"gl_account": ["This field is required."]},
            400,
            2,
            0,
        ),
        (
            {"fee": "200.90", "gl_account": "PK-123-459"},
            {"fee_type": ["This field is required."]},
            400,
            2,
            0,
        ),
        (
            {"fee_type": "FLAT_FEE", "gl_account": "PK-123-999"},
            {"fee": ["This field is required."]},
            400,
            2,
            0,
        ),
        (
            {"fee": "100.00", "fee_type": "FLAT_FEE", "gl_account": "PK-1234"},
            {
                "fee": "100.00",
                "fee_type": "FLAT_FEE",
                "gl_account": "PK-1234",
                "status": "ACTIVE",
            },
            201,
            9,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_management_fee_create(
    api_rf, user_with_permissions, data, expected_response, status_code, num_queries, obj_count
):
    """
    Testing :py:meth:`system_preferences.views.ManagementFeeViewSet.create` method.
    """

    user = user_with_permissions([("system_preferences", "managementfee")])

    with assertNumQueries(num_queries):
        url = reverse("system_preferences:management-fee-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = ManagementFeeViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        for key, value in expected_response.items():
            assert response.data[key] == value
    assert ManagementFee.objects.count() == obj_count


@pytest.mark.django_db
def test_management_fee_retrieve(api_rf, management_fee_factory, user_with_permissions):
    """
    Testing :py:meth:`system_preferences.views.ManagementFeeViewSet.retrieve` method.
    """

    user = user_with_permissions([("system_preferences", "managementfee")])
    management_fee = management_fee_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse("system_preferences:management-fee-detail", kwargs={"pk": management_fee.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = ManagementFeeViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=management_fee.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "fee",
        "fee_type",
        "get_fee_type_display",
        "gl_account",
        "status",
        "get_status_display",
        "created_at",
        "previous_fee",
        "previous_fee_type",
        "get_previous_fee_type_display",
        "created_by",
    }


@pytest.mark.parametrize(
    "data",
    (
        {"fee": "123.00"},
        {"fee_type": "BY_PERCENTAGE"},
        {"gl_account": "PK-123-456-789"},
        {"fee": "999.00", "fee_type": "FLAT_FEE"},
    ),
)
@pytest.mark.django_db
def test_management_fee_update(api_rf, management_fee_factory, user_with_permissions, data):
    """
    Testing :py:meth:`system_preferences.views.ManagementFeeViewSet.partial_update` method.
    """

    user = user_with_permissions([("system_preferences", "managementfee")])
    management_fee = management_fee_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse("system_preferences:management-fee-detail", kwargs={"pk": management_fee.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = ManagementFeeViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=management_fee.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_management_fee_delete(api_rf, management_fee_factory, user_with_permissions):
    """
    Testing :py:meth:`system_preferences.views.ManagementFeeViewSet.delete` method.
    """

    user = user_with_permissions([("system_preferences", "managementfee")])
    management_fee = management_fee_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse("system_preferences:management-fee-detail", kwargs={"pk": management_fee.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = ManagementFeeViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=management_fee.id)

    assert response.status_code == 204

    assert ManagementFee.objects.count() == 0
