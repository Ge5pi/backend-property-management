import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from lease.models import Lease
from lease.views import LeaseViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 15),
        ({"status": "ACTIVE"}, [0], 9),
        ({"unit": 0}, [0], 10),
        ({"unit__parent_property": 2}, [2], 10),
        ({"remaining_days_less_than": 20}, [1], 9),
    ),
)
@pytest.mark.django_db
def test_lease_list(api_rf, user_with_permissions, lease_factory, query_params, index_result, num_queries, freezer):
    """
    Testing :py:meth:`lease.views.LeaseViewSet.list` method.
    """
    user = user_with_permissions([("lease", "lease")])

    freezer.move_to("2021-01-20 00:00:00")
    instance_1 = lease_factory(status="ACTIVE", end_date="2021-06-01", subscription=user.associated_subscription)
    instance_2 = lease_factory(end_date="2021-01-30", subscription=user.associated_subscription)
    instance_3 = lease_factory(end_date="2021-06-01", subscription=user.associated_subscription)
    lease_factory()

    leases = [instance_1.id, instance_2.id, instance_3.id]
    units = [instance_1.unit.id, instance_2.unit.id, instance_3.unit.id]
    property_ids = [
        instance_1.unit.parent_property.id,
        instance_2.unit.parent_property.id,
        instance_3.unit.parent_property.id,
    ]

    if "unit" in query_params:
        query_params["unit"] = units[query_params["unit"]]

    if "unit__parent_property" in query_params:
        query_params["unit__parent_property"] = property_ids[query_params["unit__parent_property"]]

    with assertNumQueries(num_queries):
        url = reverse("lease:lease-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = LeaseViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [leases[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "applicant": ["This field is required."],
                "lease_type": ["This field is required."],
                "start_date": ["This field is required."],
                "end_date": ["This field is required."],
                "rent_cycle": ["This field is required."],
                "amount": ["This field is required."],
                "gl_account": ["This field is required."],
                "due_date": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "lease_type": "FIXED",
                "get_lease_type_display": "Fixed",
                "start_date": "2001-07-04",
                "end_date": "1985-04-20",
                "rent_cycle": "MONTHLY",
                "get_rent_cycle_display": "Monthly",
                "amount": "118.01",
                "gl_account": "8854",
                "description": "Trouble parent dog billion send add plant decade.",
                "due_date": "1985-07-25",
                "status": "ACTIVE",
                "get_status_display": "PENDING",
                "closed_on": "2010-04-22",
            },
            None,
            201,
            17,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_lease_create(
    api_rf,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
    applicant_factory,
):
    """
    Testing :py:meth:`lease.views.LeaseViewSet.create` method.
    """
    applicant = applicant_factory()
    user = user_with_permissions([("lease", "lease")])

    if status_code == 201:
        data["applicant"] = applicant.id

    with assertNumQueries(num_queries):
        url = reverse("lease:lease-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = LeaseViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert Lease.objects.count() == obj_count


@pytest.mark.django_db
def test_lease_retrieve(api_rf, lease_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.LeaseViewSet.retrieve` method.
    """

    user = user_with_permissions([("lease", "lease")])
    lease = lease_factory(subscription=user.associated_subscription)

    with assertNumQueries(9):
        url = reverse("lease:lease-detail", kwargs={"pk": lease.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = LeaseViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=lease.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "rental_application",
        "lease_type",
        "get_lease_type_display",
        "start_date",
        "end_date",
        "lease_template",
        "rent_cycle",
        "get_rent_cycle_display",
        "amount",
        "gl_account",
        "description",
        "due_date",
        "status",
        "get_status_display",
        "closed_on",
        "unit",
        "created_at",
        "primary_tenant",
        "property_id",
        "property_name",
        "unit_name",
        "tenant_first_name",
        "tenant_last_name",
        "owners",
        "applicant_id",
    }


@pytest.mark.django_db
def test_lease_update(api_rf, lease_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.LeaseViewSet.partial_update` method.
    """

    user = user_with_permissions([("lease", "lease")])
    lease = lease_factory(subscription=user.associated_subscription)
    data = {
        "lease_type": "FIXED",
        "get_lease_type_display": "Fixed",
        "start_date": "2001-07-04",
        "end_date": "1985-04-20",
        "rent_cycle": "MONTHLY",
        "get_rent_cycle_display": "Monthly",
        "amount": "118.01",
        "gl_account": "8854",
        "description": "Trouble parent dog billion send add plant decade.",
        "due_date": "1985-07-25",
        "status": "ACTIVE",
        "closed_on": "2010-04-22",
    }

    with assertNumQueries(11):
        url = reverse("lease:lease-detail", kwargs={"pk": lease.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = LeaseViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=lease.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_lease_delete(api_rf, lease_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.LeaseViewSet.delete` method.
    """

    user = user_with_permissions([("lease", "lease")])
    lease = lease_factory(status="CLOSED", subscription=user.associated_subscription)

    with assertNumQueries(17):
        url = reverse("lease:lease-detail", kwargs={"pk": lease.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = LeaseViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=lease.id)

    assert response.status_code == 204

    assert Lease.objects.count() == 0


@pytest.mark.django_db
def test_lease_close(api_rf, lease_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.LeaseViewSet.close` method.
    """

    user = user_with_permissions([("lease", "lease")])
    lease = lease_factory(status="ACTIVE", subscription=user.associated_subscription)

    with assertNumQueries(9):
        url = reverse("lease:lease-close", kwargs={"pk": lease.id})
        request = api_rf.post(url, format="json")
        request.user = user
        view = LeaseViewSet.as_view({"post": "close"})
        response = view(request, pk=lease.id)

    assert response.status_code == 200
    assert Lease.objects.get(id=lease.id).status == "CLOSED"


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "applicant": ["This field is required."],
                "lease_type": ["This field is required."],
                "start_date": ["This field is required."],
                "end_date": ["This field is required."],
                "rent_cycle": ["This field is required."],
                "amount": ["This field is required."],
                "gl_account": ["This field is required."],
                "due_date": ["This field is required."],
            },
            400,
            6,
            1,
        ),
        (
            {
                "lease_type": "FIXED",
                "get_lease_type_display": "Fixed",
                "start_date": "2001-07-04",
                "end_date": "1985-04-20",
                "rent_cycle": "MONTHLY",
                "get_rent_cycle_display": "Monthly",
                "amount": "118.01",
                "gl_account": "8854",
                "description": "Trouble parent dog billion send add plant decade.",
                "due_date": "1985-07-25",
                "status": "ACTIVE",
                "get_status_display": "PENDING",
                "closed_on": "2010-04-22",
            },
            None,
            201,
            20,
            2,
        ),
    ),
)
@pytest.mark.django_db
def test_lease_renewal(
    api_rf, user_with_permissions, data, expected_response, status_code, num_queries, obj_count, lease_factory
):
    """
    Testing :py:meth:`lease.views.LeaseViewSet.renewal` method.
    """
    user = user_with_permissions([("lease", "lease")])
    lease = lease_factory(status="ACTIVE", subscription=user.associated_subscription)

    if status_code == 201:
        data["applicant"] = lease.rental_application.applicant.id

    with assertNumQueries(num_queries):
        url = reverse("lease:lease-renewal", kwargs={"pk": lease.id})
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = LeaseViewSet.as_view({"post": "renewal"})
        response = view(request, pk=lease.id)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert Lease.objects.count() == obj_count
