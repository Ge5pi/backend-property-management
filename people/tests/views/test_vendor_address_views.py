import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from people.models import VendorAddress
from people.views import VendorAddressByVendorListAPIView, VendorAddressViewSet


@pytest.mark.django_db
def test_vendor_address_list(
    api_rf,
    user_with_permissions,
    vendor_address_factory,
    vendor_factory,
):
    """
    Testing :py:meth:`people.views.VendorAddressByVendorListAPIView.list` method.
    """
    user = user_with_permissions([("people", "vendoraddress")])

    vendor = vendor_factory()
    vendor_address_1 = vendor_address_factory(vendor=vendor, subscription=user.associated_subscription)
    vendor_address_2 = vendor_address_factory(vendor=vendor, subscription=user.associated_subscription)
    vendor_address_3 = vendor_address_factory(vendor=vendor, subscription=user.associated_subscription)
    vendor_address_factory()

    vendor_addresses = [
        vendor_address_1.id,
        vendor_address_2.id,
        vendor_address_3.id,
    ]
    index_result = [2, 1, 0]

    with assertNumQueries(3):
        url = reverse("people:vendor-address-by-vendor", kwargs={"vendor_id": vendor.id})
        request = api_rf.get(url, {}, format="json")
        request.user = user
        view = VendorAddressByVendorListAPIView.as_view()
        response = view(request, vendor_id=vendor.id)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [vendor_addresses[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "street_address": ["This field is required."],
                "city": ["This field is required."],
                "state": ["This field is required."],
                "country": ["This field is required."],
                "zip": ["This field is required."],
                "vendor": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "street_address": "07198 David Plains",
                "city": "New Jennifer",
                "state": "Oregon",
                "country": "Swaziland",
                "zip": "58050",
                "vendor": 1,
            },
            None,
            201,
            4,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_vendor_address_create(
    api_rf,
    vendor_factory,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`people.views.VendorAddressViewSet.create` method.
    """

    user = user_with_permissions([("people", "vendoraddress")])
    vendor = vendor_factory()

    if status_code == 201:
        data["vendor"] = vendor.id

    with assertNumQueries(num_queries):
        url = reverse("people:vendor_address-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = VendorAddressViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert VendorAddress.objects.count() == obj_count


@pytest.mark.django_db
def test_vendor_address_retrieve(api_rf, vendor_address_factory, user_with_permissions):
    """
    Testing :py:meth:`people.views.VendorAddressViewSet.retrieve` method.
    """

    user = user_with_permissions([("people", "vendoraddress")])
    vendor_address = vendor_address_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse(
            "people:vendor_address-detail",
            kwargs={"pk": vendor_address.id},
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = VendorAddressViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=vendor_address.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "street_address",
        "city",
        "state",
        "country",
        "zip",
        "vendor",
    }


@pytest.mark.django_db
def test_vendor_address_update(api_rf, vendor_address_factory, user_with_permissions, vendor_factory):
    """
    Testing :py:meth:`people.views.VendorAddressViewSet.partial_update` method.
    """

    user = user_with_permissions([("people", "vendoraddress")])
    vendor_address = vendor_address_factory(subscription=user.associated_subscription)
    data = {
        "street_address": "07198 David Plains",
        "city": "New Jennifer",
        "state": "Oregon",
        "country": "Swaziland",
        "zip": "58050",
        "vendor": vendor_address.vendor.id,
    }

    with assertNumQueries(5):
        url = reverse(
            "people:vendor_address-detail",
            kwargs={"pk": vendor_address.id},
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = VendorAddressViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=vendor_address.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_vendor_address_delete(api_rf, vendor_address_factory, user_with_permissions):
    """
    Testing :py:meth:`people.views.VendorAddressViewSet.delete` method.
    """

    user = user_with_permissions([("people", "vendoraddress")])
    vendor_address = vendor_address_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse(
            "people:vendor_address-detail",
            kwargs={"pk": vendor_address.id},
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = VendorAddressViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=vendor_address.id)

    assert response.status_code == 204

    assert VendorAddress.objects.count() == 0
