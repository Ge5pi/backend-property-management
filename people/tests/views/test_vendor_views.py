import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from people.models import Vendor
from people.views import VendorViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"search": "Michael"}, [0], 3),
        ({"search": "Lawrence"}, [1], 3),
        ({"search": "Wright-Brennan"}, [2], 3),
        ({"search": "vnd-2"}, [1], 3),
        ({"ordering": "pk"}, [0, 1, 2], 3),
        ({"ordering": "-pk"}, [2, 1, 0], 3),
        ({"ordering": "first_name"}, [2, 1, 0], 3),
        ({"ordering": "-first_name"}, [0, 1, 2], 3),
        ({"ordering": "last_name"}, [2, 1, 0], 3),
        ({"ordering": "-last_name"}, [0, 1, 2], 3),
        ({"ordering": "company_name"}, [1, 0, 2], 3),
        ({"ordering": "-company_name"}, [2, 0, 1], 3),
        ({"ordering": "slug"}, [0, 1, 2], 3),
        ({"ordering": "-slug"}, [2, 1, 0], 3),
    ),
)
@pytest.mark.django_db
def test_vendor_list(
    api_rf,
    user_with_permissions,
    vendor_factory,
    query_params,
    index_result,
    num_queries,
):
    """
    Testing :py:meth:`people.views.VendorViewSet.list` method.
    """
    user = user_with_permissions([("people", "vendor")])

    vendor_1 = vendor_factory(
        first_name="Michael",
        last_name="Rhodes",
        company_name="Stokes-Forbes",
        subscription=user.associated_subscription,
    )
    vendor_2 = vendor_factory(
        first_name="John", last_name="Lawrence", company_name="Meyer Inc", subscription=user.associated_subscription
    )
    vendor_3 = vendor_factory(
        first_name="Alex", last_name="Chan", company_name="Wright-Brennan", subscription=user.associated_subscription
    )
    vendor_factory()

    if query_params.get("search") and query_params["search"].startswith("vnd-"):
        query_params["search"] = f"vnd-{vendor_2.id}"

    vendors = [
        vendor_1.id,
        vendor_2.id,
        vendor_3.id,
    ]

    with assertNumQueries(num_queries):
        url = reverse("people:vendor-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = VendorViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [vendors[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "first_name": ["This field is required."],
                "last_name": ["This field is required."],
                "company_name": ["This field is required."],
                "use_company_name_as_display_name": ["This field is required."],
                "vendor_type": ["This field is required."],
                "gl_account": ["This field is required."],
                "personal_contact_numbers": ["This field is required."],
                "business_contact_numbers": ["This field is required."],
                "personal_emails": ["This field is required."],
                "business_emails": ["This field is required."],
                "website": ["This field is required."],
                "insurance_provide_name": ["This field is required."],
                "insurance_policy_number": ["This field is required."],
                "insurance_expiry_date": ["This field is required."],
                "tax_identity_type": ["This field is required."],
                "tax_payer_id": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "first_name": "Steven",
                "last_name": "Ward",
                "company_name": "Lane-Becker",
                "use_company_name_as_display_name": True,
                "vendor_type": 1,
                "gl_account": "16392591156",
                "personal_contact_numbers": ["+923111234455"],
                "business_contact_numbers": ["+923111234455"],
                "personal_emails": ["michelewilson@example.net"],
                "business_emails": ["ahayes@example.net"],
                "website": "http://www.george.net/",
                "insurance_provide_name": "Hall-Gilbert",
                "insurance_policy_number": "452972008732",
                "insurance_expiry_date": "1976-09-20",
                "tax_identity_type": "SSN",
                "tax_payer_id": "9396",
                "vendor_type_name": "single",
            },
            None,
            201,
            4,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_vendor_create(
    api_rf,
    user_with_permissions,
    vendor_type_factory,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`people.views.VendorViewSet.create` method.
    """

    user = user_with_permissions([("people", "vendor")])
    vendor_type = vendor_type_factory()

    if status_code == 201:
        data["vendor_type"] = vendor_type.id

    with assertNumQueries(num_queries):
        url = reverse("people:vendor-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = VendorViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert Vendor.objects.count() == obj_count


@pytest.mark.django_db
def test_vendor_retrieve(api_rf, vendor_factory, user_with_permissions):
    """
    Testing :py:meth:`people.views.VendorViewSet.retrieve` method.
    """

    user = user_with_permissions([("people", "vendor")])
    vendor = vendor_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse("people:vendor-detail", kwargs={"pk": vendor.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = VendorViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=vendor.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "first_name",
        "last_name",
        "slug",
        "company_name",
        "use_company_name_as_display_name",
        "vendor_type",
        "gl_account",
        "personal_contact_numbers",
        "business_contact_numbers",
        "personal_emails",
        "business_emails",
        "website",
        "insurance_provide_name",
        "insurance_policy_number",
        "insurance_expiry_date",
        "tax_identity_type",
        "get_tax_identity_type_display",
        "tax_payer_id",
        "vendor_type_name",
    }


@pytest.mark.django_db
def test_vendor_update(api_rf, vendor_factory, user_with_permissions):
    """
    Testing :py:meth:`people.views.VendorViewSet.partial_update` method.
    """

    user = user_with_permissions([("people", "vendor")])
    vendor = vendor_factory(subscription=user.associated_subscription)
    data = {
        "first_name": "Steven",
        "last_name": "Ward",
        "company_name": "Lane-Becker",
        "use_company_name_as_display_name": True,
        "vendor_type": vendor.vendor_type.id,
        "gl_account": "16392591156",
        "personal_contact_numbers": ["+923111234455"],
        "business_contact_numbers": ["+923111234455"],
        "personal_emails": ["michelewilson@example.net"],
        "business_emails": ["ahayes@example.net"],
        "website": "http://www.george.net/",
        "insurance_provide_name": "Hall-Gilbert",
        "insurance_policy_number": "452972008732",
        "insurance_expiry_date": "1976-09-20",
        "tax_identity_type": "SSN",
        "tax_payer_id": "9396",
    }

    with assertNumQueries(5):
        url = reverse("people:vendor-detail", kwargs={"pk": vendor.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = VendorViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=vendor.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_vendor_delete(api_rf, vendor_factory, user_with_permissions):
    """
    Testing :py:meth:`people.views.VendorViewSet.delete` method.
    """

    user = user_with_permissions([("people", "vendor")])
    vendor = vendor_factory(subscription=user.associated_subscription)

    with assertNumQueries(12):
        url = reverse("people:vendor-detail", kwargs={"pk": vendor.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = VendorViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=vendor.id)

    assert response.status_code == 204

    assert Vendor.objects.count() == 0
