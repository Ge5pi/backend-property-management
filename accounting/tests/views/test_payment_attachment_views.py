import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from accounting.models import PaymentAttachment
from accounting.views import PaymentAttachmentViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"payment": True}, [1, 0], 4),
    ),
)
@pytest.mark.django_db
def test_payment_attachment_list(
    api_rf, query_params, index_result, num_queries, user_with_permissions, payment_attachment_factory, payment_factory
):
    """
    Testing :py:meth:`accounting.views.PaymentAttachmentByPaymentListAPIView` method.
    """
    user = user_with_permissions([("accounting", "paymentattachment")])
    payment = payment_factory(subscription=user.associated_subscription)

    if query_params.get("payment", False):
        query_params["payment"] = payment.id

    instance_1 = payment_attachment_factory(payment=payment, subscription=user.associated_subscription)
    instance_2 = payment_attachment_factory(payment=payment, subscription=user.associated_subscription)
    instance_3 = payment_attachment_factory(subscription=user.associated_subscription)
    payment_attachment_factory()

    payment_attachments = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("accounting:payment-attachment-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = PaymentAttachmentViewSet.as_view({"get": "list"})
        response = view(request, payment_id=payment.id)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [payment_attachments[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "payment": ["This field is required."],
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
def test_payment_attachment_create(
    api_rf,
    payment_factory,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`accounting.views.PaymentAttachmentViewSet.create` method.
    """

    user = user_with_permissions([("accounting", "paymentattachment")])
    payment = payment_factory(
        subscription=user.associated_subscription,
    )

    if status_code == 201:
        data["payment"] = payment.id

    with assertNumQueries(num_queries):
        url = reverse("accounting:payment-attachment-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = PaymentAttachmentViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert PaymentAttachment.objects.count() == obj_count


@pytest.mark.django_db
def test_payment_attachment_retrieve(api_rf, payment_attachment_factory, payment_factory, user_with_permissions):
    """
    Testing :py:meth:`accounting.views.PaymentAttachmentViewSet.retrieve` method.
    """

    user = user_with_permissions([("accounting", "paymentattachment")])
    payment_attachment = payment_attachment_factory(
        subscription=user.associated_subscription,
    )

    with assertNumQueries(3):
        url = reverse(
            "accounting:payment-attachment-detail",
            kwargs={"pk": payment_attachment.id},
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = PaymentAttachmentViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=payment_attachment.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "name",
        "created_by",
        "file",
        "payment",
        "file_type",
        "updated_at",
    }


@pytest.mark.django_db
def test_payment_attachment_update(api_rf, payment_attachment_factory, user_with_permissions, payment_factory):
    """
    Testing :py:meth:`accounting.views.PaymentAttachmentViewSet.partial_update` method.
    """

    user = user_with_permissions([("accounting", "paymentattachment")])
    payment = payment_factory(
        subscription=user.associated_subscription,
    )
    payment_attachment = payment_attachment_factory(
        subscription=user.associated_subscription,
    )
    data = {
        "payment": payment.id,
        "file": "Agreement.pdf",
        "name": "Agreement",
        "file_type": "pdf",
    }

    with assertNumQueries(5):
        url = reverse(
            "accounting:payment-attachment-detail",
            kwargs={"pk": payment_attachment.id},
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = PaymentAttachmentViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=payment_attachment.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_payment_attachment_delete(api_rf, payment_attachment_factory, user_with_permissions, payment_factory):
    """
    Testing :py:meth:`accounting.views.PaymentAttachmentViewSet.delete` method.
    """

    user = user_with_permissions([("accounting", "paymentattachment")])
    payment_attachment = payment_attachment_factory(
        subscription=user.associated_subscription,
    )

    with assertNumQueries(4):
        url = reverse(
            "accounting:payment-attachment-detail",
            kwargs={"pk": payment_attachment.id},
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = PaymentAttachmentViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=payment_attachment.id)

    assert response.status_code == 204

    assert PaymentAttachment.objects.count() == 0
