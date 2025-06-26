import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from accounting.models import Charge
from accounting.views import ChargeViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"ordering": "created_at"}, [0, 1, 2], 3),
        ({"ordering": "-created_at"}, [2, 1, 0], 3),
        ({"ordering": "title"}, [1, 2, 0], 3),
        ({"ordering": "-title"}, [0, 2, 1], 3),
        ({"ordering": "amount"}, [2, 0, 1], 3),
        ({"ordering": "-amount"}, [1, 0, 2], 3),
        ({"ordering": "status"}, [2, 0, 1], 3),
        ({"ordering": "-status"}, [1, 0, 2], 3),
        ({"search": "Perform such current"}, [0], 3),
        ({"search": "Almost affect on"}, [1], 3),
        ({"search": "Amount they collection those city"}, [2], 3),
        ({"search": "John Maxwell"}, [2], 3),
        ({"search": "Doe"}, [2], 3),
        ({"search": "Accept tree public hit race"}, [2], 3),
        ({"status": "VERIFIED"}, [1], 3),
        ({"invoice": 0}, [0], 4),
        ({"parent_property": 0}, [1], 4),
        ({"unit": 0}, [0], 4),
        ({"created_at__gte": "2023-01-02"}, [2, 1], 3),
        ({"created_at__lte": "2023-01-04"}, [1, 0], 3),
    ),
)
@pytest.mark.django_db
def test_charge_list(
    api_rf,
    user_with_permissions,
    charge_factory,
    property_factory,
    unit_factory,
    applicant_factory,
    rental_application_factory,
    lease_factory,
    query_params,
    index_result,
    num_queries,
    freezer,
    invoice_factory,
):
    """
    Testing :py:meth:`accounting.views.ChargeViewSet.list` method.
    """
    user = user_with_permissions([("accounting", "charge")])
    prop = property_factory(name="Property 1")
    unit = unit_factory()
    applicant = applicant_factory(first_name="John Maxwell", last_name="Doe")
    rental_application = rental_application_factory(applicant=applicant)
    lease = lease_factory(rental_application=rental_application)
    invoice = invoice_factory(lease=lease, subscription=user.associated_subscription)

    if "invoice" in query_params:
        query_params["invoice"] = invoice.id

    if "parent_property" in query_params:
        query_params["parent_property"] = prop.id

    if "unit" in query_params:
        query_params["unit"] = unit.id

    freezer.move_to("2023-01-01 00:00:00")
    instance_1 = charge_factory(
        title="Perform such current however.",
        unit=unit,
        amount="1000.00",
        status="UNPAID",
        subscription=user.associated_subscription,
        invoice=invoice,
    )
    freezer.move_to("2023-01-03 00:00:00")
    instance_2 = charge_factory(
        title="Almost affect one theory",
        amount="2000.00",
        status="VERIFIED",
        parent_property=prop,
        subscription=user.associated_subscription,
    )
    freezer.move_to("2023-01-05 00:00:00")
    instance_3 = charge_factory(
        title="Amount they collection those city tend able.",
        description="Accept tree public hit race",
        tenant_id=lease.primary_tenant.id,
        amount="500.00",
        status="NOT_VERIFIED",
        subscription=user.associated_subscription,
    )
    charge_factory()

    charges = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("accounting:charge-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = ChargeViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [charges[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "title": ["This field is required."],
                "description": ["This field is required."],
                "charge_type": ["This field is required."],
                "amount": ["This field is required."],
                "gl_account": ["This field is required."],
                "tenant": ["This field is required."],
                "parent_property": ["This field is required."],
                "unit": ["This field is required."],
                "notes": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "status": "UNPAID",
                "title": "Chance focus floor provide reach good writer. Drive watch say consumer business out test",
                "description": "Defense save necessary at still.",
                "charge_type": "ONE_TIME",
                "amount": "848.35",
                "gl_account": "92392872.",
                "notes": "Language church surface really go. Offer wonder teacher turn evidence concern occur.",
            },
            None,
            201,
            6,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_charge_create(
    api_rf,
    unit_factory,
    tenant_factory,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`accounting.views.ChargeViewSet.create` method.
    """

    user = user_with_permissions([("accounting", "charge")])
    unit = unit_factory(subscription=user.associated_subscription)
    tenant = tenant_factory(subscription=user.associated_subscription)

    if status_code == 201:
        data["unit"] = unit.id
        data["tenant"] = tenant.id
        data["parent_property"] = unit.parent_property.id

    with assertNumQueries(num_queries):
        url = reverse("accounting:charge-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = ChargeViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert Charge.objects.count() == obj_count


@pytest.mark.django_db
def test_charge_retrieve(api_rf, charge_factory, user_with_permissions):
    """
    Testing :py:meth:`accounting.views.ChargeViewSet.retrieve` method.
    """

    user = user_with_permissions([("accounting", "charge")])
    charge = charge_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse("accounting:charge-detail", kwargs={"pk": charge.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = ChargeViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=charge.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "slug",
        "title",
        "description",
        "charge_type",
        "get_charge_type_display",
        "status",
        "get_status_display",
        "amount",
        "gl_account",
        "tenant",
        "parent_property",
        "unit",
        "notes",
        "created_at",
        "parent_charge",
        "invoice",
        "property_name",
        "unit_name",
        "tenant_first_name",
        "tenant_last_name",
    }


@pytest.mark.django_db
def test_charge_update(api_rf, charge_factory, tenant_factory, unit_factory, user_with_permissions):
    """
    Testing :py:meth:`accounting.views.ChargeViewSet.partial_update` method.
    """

    user = user_with_permissions([("accounting", "charge")])
    charge = charge_factory(subscription=user.associated_subscription)
    data = {
        "status": "UNPAID",
        "title": "Chance focus floor provide reach good writer. Drive watch say consumer business out test",
        "description": "Defense save necessary at still.",
        "charge_type": "ONE_TIME",
        "amount": "848.35",
        "gl_account": "92392872.",
        "tenant": charge.tenant.id,
        "parent_property": charge.parent_property.id,
        "unit": charge.unit.id,
        "notes": "Language church surface really go. Offer wonder teacher turn evidence concern occur.",
    }

    with assertNumQueries(7):
        url = reverse("accounting:charge-detail", kwargs={"pk": charge.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = ChargeViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=charge.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_charge_delete(api_rf, charge_factory, user_with_permissions):
    """
    Testing :py:meth:`accounting.views.ChargeViewSet.delete` method.
    """

    user = user_with_permissions([("accounting", "charge")])
    charge = charge_factory(subscription=user.associated_subscription)

    with assertNumQueries(6):
        url = reverse("accounting:charge-detail", kwargs={"pk": charge.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = ChargeViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=charge.id)

    assert response.status_code == 204

    assert Charge.objects.count() == 0
