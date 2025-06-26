import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from accounting.models import ChargeAttachment
from accounting.views import ChargeAttachmentByChargeListAPIView, ChargeAttachmentViewSet


@pytest.mark.django_db
def test_charge_attachment_list(api_rf, user_with_permissions, charge_attachment_factory, charge_factory):
    """
    Testing :py:meth:`accounting.views.ChargeAttachmentByChargeListAPIView` method.
    """
    user = user_with_permissions(
        [("accounting", "chargeattachment")],
    )
    charge = charge_factory(
        subscription=user.associated_subscription,
    )
    instance_1 = charge_attachment_factory(charge=charge, subscription=user.associated_subscription)
    instance_2 = charge_attachment_factory(charge=charge, subscription=user.associated_subscription)
    instance_3 = charge_attachment_factory(charge=charge, subscription=user.associated_subscription)
    charge_attachment_factory()

    index_result = [2, 1, 0]

    charge_attachments = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(3):
        url = reverse("accounting:charge-attachment-list", kwargs={"charge_id": 200})
        request = api_rf.get(url, {}, format="json")
        request.user = user
        view = ChargeAttachmentByChargeListAPIView.as_view()
        response = view(request, charge_id=charge.id)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [charge_attachments[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "charge": ["This field is required."],
                "file": ["This field is required."],
                "name": ["This field is required."],
                "file_type": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
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
def test_charge_attachment_create(
    api_rf,
    charge_factory,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`accounting.views.ChargeAttachmentViewSet.create` method.
    """

    user = user_with_permissions([("accounting", "chargeattachment")])
    charge = charge_factory(
        subscription=user.associated_subscription,
    )

    if status_code == 201:
        data["charge"] = charge.id

    with assertNumQueries(num_queries):
        url = reverse("accounting:charge-attachment-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = ChargeAttachmentViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert ChargeAttachment.objects.count() == obj_count


@pytest.mark.django_db
def test_charge_attachment_retrieve(api_rf, charge_attachment_factory, charge_factory, user_with_permissions):
    """
    Testing :py:meth:`accounting.views.ChargeAttachmentViewSet.retrieve` method.
    """

    user = user_with_permissions([("accounting", "chargeattachment")])
    charge_attachment = charge_attachment_factory(
        subscription=user.associated_subscription,
    )

    with assertNumQueries(3):
        url = reverse(
            "accounting:charge-attachment-detail",
            kwargs={"pk": charge_attachment.id},
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = ChargeAttachmentViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=charge_attachment.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "name",
        "created_by",
        "file",
        "charge",
        "file_type",
        "updated_at",
    }


@pytest.mark.django_db
def test_charge_attachment_update(api_rf, charge_attachment_factory, user_with_permissions, charge_factory):
    """
    Testing :py:meth:`accounting.views.ChargeAttachmentViewSet.partial_update` method.
    """

    user = user_with_permissions([("accounting", "chargeattachment")])
    charge = charge_factory(
        subscription=user.associated_subscription,
    )
    charge_attachment = charge_attachment_factory(
        subscription=user.associated_subscription,
    )
    data = {
        "charge": charge.id,
        "file": "Agreement.pdf",
        "name": "Agreement",
        "file_type": "pdf",
    }

    with assertNumQueries(5):
        url = reverse(
            "accounting:charge-attachment-detail",
            kwargs={"pk": charge_attachment.id},
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = ChargeAttachmentViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=charge_attachment.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_charge_attachment_delete(api_rf, charge_attachment_factory, user_with_permissions, charge_factory):
    """
    Testing :py:meth:`accounting.views.ChargeAttachmentViewSet.delete` method.
    """

    user = user_with_permissions([("accounting", "chargeattachment")])
    charge_attachment = charge_attachment_factory(
        subscription=user.associated_subscription,
    )

    with assertNumQueries(4):
        url = reverse(
            "accounting:charge-attachment-detail",
            kwargs={"pk": charge_attachment.id},
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = ChargeAttachmentViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=charge_attachment.id)

    assert response.status_code == 204

    assert ChargeAttachment.objects.count() == 0
