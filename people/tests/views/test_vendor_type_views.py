import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from people.models import VendorType
from people.views import VendorTypeViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"search": "Manufacturers"}, [0], 3),
        ({"search": "Republican wide"}, [1], 3),
        ({"search": "vnt-3"}, [2], 3),
        ({"ordering": "pk"}, [0, 1, 2], 3),
        ({"ordering": "-pk"}, [2, 1, 0], 3),
        ({"ordering": "name"}, [0, 2, 1], 3),
        ({"ordering": "-name"}, [1, 2, 0], 3),
        ({"ordering": "description"}, [0, 1, 2], 3),
        ({"ordering": "-description"}, [2, 1, 0], 3),
        ({"ordering": "slug"}, [0, 1, 2], 3),
        ({"ordering": "-slug"}, [2, 1, 0], 3),
        ({"ordering": "vendor_count"}, [1, 2, 0], 3),
        ({"ordering": "-vendor_count"}, [0, 1, 2], 3),
    ),
)
@pytest.mark.django_db
def test_vendor_type_list(
    api_rf,
    user_with_permissions,
    vendor_type_factory,
    vendor_factory,
    query_params,
    index_result,
    num_queries,
):
    """
    Testing :py:meth:`people.views.VendorTypeViewSet.list` method.
    """
    user = user_with_permissions([("people", "vendortype")])

    vendor_type_1 = vendor_type_factory(
        name="Manufacturers", description="Area knowledge remain", subscription=user.associated_subscription
    )
    vendor_type_2 = vendor_type_factory(
        name="Wholesalers",
        description="Eye soon Republican wide popular window",
        subscription=user.associated_subscription,
    )
    vendor_type_3 = vendor_type_factory(
        name="Retailers", description="On though expert", subscription=user.associated_subscription
    )
    vendor_type_factory()

    if query_params.get("search") and query_params["search"].startswith("vnt-"):
        query_params["search"] = f"vnt-{vendor_type_3.id}"

    vendor_factory(vendor_type=vendor_type_1)

    vendor_types = [
        vendor_type_1.id,
        vendor_type_2.id,
        vendor_type_3.id,
    ]

    with assertNumQueries(num_queries):
        url = reverse("people:vendor_type-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = VendorTypeViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [vendor_types[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "description": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "name": "Supplier",
                "description": "lorem ipsum dolor",
            },
            None,
            201,
            3,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_vendor_type_create(
    api_rf,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`people.views.VendorTypeViewSet.create` method.
    """

    user = user_with_permissions([("people", "vendortype")])

    with assertNumQueries(num_queries):
        url = reverse("people:vendor_type-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = VendorTypeViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert VendorType.objects.count() == obj_count


@pytest.mark.django_db
def test_vendor_type_retrieve(api_rf, vendor_type_factory, user_with_permissions):
    """
    Testing :py:meth:`people.views.VendorTypeViewSet.retrieve` method.
    """

    user = user_with_permissions([("people", "vendortype")])
    vendor_type = vendor_type_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse("people:vendor_type-detail", kwargs={"pk": vendor_type.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = VendorTypeViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=vendor_type.id)

    assert response.status_code == 200

    assert response.data.keys() == {"id", "name", "slug", "description", "vendor_count"}


@pytest.mark.django_db
def test_vendor_type_update(api_rf, vendor_type_factory, user_with_permissions):
    """
    Testing :py:meth:`people.views.VendorTypeViewSet.partial_update` method.
    """

    user = user_with_permissions([("people", "vendortype")])
    vendor_type = vendor_type_factory(subscription=user.associated_subscription)
    data = {
        "name": "Supplier",
        "description": "lorem ipsum dolor",
    }

    with assertNumQueries(4):
        url = reverse("people:vendor_type-detail", kwargs={"pk": vendor_type.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = VendorTypeViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=vendor_type.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_vendor_type_delete(api_rf, vendor_type_factory, user_with_permissions):
    """
    Testing :py:meth:`people.views.VendorTypeViewSet.delete` method.
    """

    user = user_with_permissions([("people", "vendortype")])
    vendor_type = vendor_type_factory(subscription=user.associated_subscription)

    with assertNumQueries(6):
        url = reverse("people:vendor_type-detail", kwargs={"pk": vendor_type.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = VendorTypeViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=vendor_type.id)

    assert response.status_code == 204

    assert VendorType.objects.count() == 0
