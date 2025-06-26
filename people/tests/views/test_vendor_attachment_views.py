import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from people.models import VendorAttachment
from people.views import VendorAttachmentViewSet


@pytest.mark.django_db
def test_vendor_attachment_list(
    api_rf,
    user_with_permissions,
    vendor_attachment_factory,
    vendor_factory,
):
    """
    Testing :py:meth:`people.views.VendorAttachmentViewSet.list` method.
    """
    user = user_with_permissions([("people", "vendorattachment")])

    vendor = vendor_factory()
    vendor_attachment_1 = vendor_attachment_factory(vendor=vendor, subscription=user.associated_subscription)
    vendor_attachment_2 = vendor_attachment_factory(vendor=vendor, subscription=user.associated_subscription)
    vendor_attachment_3 = vendor_attachment_factory(vendor=vendor, subscription=user.associated_subscription)
    vendor_attachment_factory()

    vendor_attachments = [
        vendor_attachment_1.id,
        vendor_attachment_2.id,
        vendor_attachment_3.id,
    ]
    index_result = [2, 1, 0]

    with assertNumQueries(3):
        url = reverse("people:vendor_attachment-list", kwargs={"vendor_id": vendor.id})
        request = api_rf.get(url, {}, format="json")
        request.user = user
        view = VendorAttachmentViewSet.as_view({"get": "list"})
        response = view(request, vendor_id=vendor.id)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [vendor_attachments[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "file": ["This field is required."],
                "vendor": ["This field is required."],
                "file_type": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "vendor": 1,
                "file": "Agreement.pdf",
                "name": "Agreement",
                "file_type": "pdf",
            },
            None,
            201,
            8,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_vendor_attachment_create(
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
    Testing :py:meth:`people.views.VendorAttachmentViewSet.create` method.
    """

    user = user_with_permissions([("people", "vendorattachment")])
    vendor = vendor_factory()

    if status_code == 201:
        data["vendor"] = vendor.id

    with assertNumQueries(num_queries):
        url = reverse("people:vendor_attachment-list", kwargs={"vendor_id": vendor.id})
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = VendorAttachmentViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert VendorAttachment.objects.count() == obj_count


@pytest.mark.django_db
def test_vendor_attachment_retrieve(api_rf, vendor_attachment_factory, user_with_permissions):
    """
    Testing :py:meth:`people.views.VendorAttachmentViewSet.retrieve` method.
    """

    user = user_with_permissions([("people", "vendorattachment")])
    vendor_attachment = vendor_attachment_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse(
            "people:vendor_attachment-detail",
            kwargs={
                "pk": vendor_attachment.id,
                "vendor_id": vendor_attachment.vendor.id,
            },
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = VendorAttachmentViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=vendor_attachment.id, vendor_id=vendor_attachment.vendor.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "name",
        "created_by",
        "file",
        "vendor",
        "file_type",
        "updated_at",
    }


@pytest.mark.django_db
def test_vendor_attachment_update(api_rf, vendor_attachment_factory, user_with_permissions, vendor_factory):
    """
    Testing :py:meth:`people.views.VendorAttachmentViewSet.partial_update` method.
    """

    user = user_with_permissions([("people", "vendorattachment")])
    vendor_attachment = vendor_attachment_factory(subscription=user.associated_subscription)
    data = {
        "vendor": vendor_attachment.vendor.id,
        "file": "Agreement.pdf",
        "name": "Agreement",
        "file_type": "pdf",
    }

    with assertNumQueries(5):
        url = reverse(
            "people:vendor_attachment-detail",
            kwargs={
                "pk": vendor_attachment.id,
                "vendor_id": vendor_attachment.vendor.id,
            },
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = VendorAttachmentViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=vendor_attachment.id, vendor_id=vendor_attachment.vendor.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_vendor_attachment_delete(api_rf, vendor_attachment_factory, user_with_permissions):
    """
    Testing :py:meth:`people.views.VendorAttachmentViewSet.delete` method.
    """

    user = user_with_permissions([("people", "vendorattachment")])
    vendor_attachment = vendor_attachment_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse(
            "people:vendor_attachment-detail",
            kwargs={
                "pk": vendor_attachment.id,
                "vendor_id": vendor_attachment.vendor.id,
            },
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = VendorAttachmentViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=vendor_attachment.id, vendor_id=vendor_attachment.vendor.id)

    assert response.status_code == 204

    assert VendorAttachment.objects.count() == 0
