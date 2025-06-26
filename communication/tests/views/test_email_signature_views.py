import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from communication.models import EmailSignature
from communication.views import EmailSignatureViewSet, MyEmailSignatureViewSet


@pytest.mark.django_db
def test_email_signature_list(api_rf, user_with_permissions, email_signature_factory):
    """
    Testing :py:meth:`communication.views.EmailSignatureViewSet.list` method.
    """
    user = user_with_permissions([("communication", "emailsignature")])

    instance_1 = email_signature_factory(subscription=user.associated_subscription)
    instance_2 = email_signature_factory(subscription=user.associated_subscription)
    instance_3 = email_signature_factory(subscription=user.associated_subscription)
    email_signature_factory()

    email_signatures = [instance_1.id, instance_2.id, instance_3.id]
    index_result = [2, 1, 0]

    with assertNumQueries(3):
        url = reverse("communication:email-signature-list")
        request = api_rf.get(url, {}, format="json")
        request.user = user
        view = EmailSignatureViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [email_signatures[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "text": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "image": "test.jpg",
            },
            None,
            201,
            3,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_email_signature_create(
    api_rf, user_with_permissions, data, expected_response, status_code, num_queries, obj_count
):
    """
    Testing :py:meth:`communication.views.EmailSignatureViewSet6.create` method.
    """

    user = user_with_permissions([("communication", "emailsignature")])

    with assertNumQueries(num_queries):
        url = reverse("communication:email-signature-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = EmailSignatureViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert EmailSignature.objects.count() == obj_count


@pytest.mark.django_db
def test_email_signature_retrieve(api_rf, email_signature_factory, user_with_permissions):
    """
    Testing :py:meth:`communication.views.EmailSignatureViewSet.retrieve` method.
    """

    user = user_with_permissions([("communication", "emailsignature")])
    email_signature = email_signature_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse("communication:email-signature-detail", kwargs={"pk": email_signature.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = EmailSignatureViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=email_signature.id)

    assert response.status_code == 200

    assert response.data.keys() == {"id", "text", "image"}


@pytest.mark.django_db
def test_email_signature_update(api_rf, email_signature_factory, user_with_permissions):
    """
    Testing :py:meth:`communication.views.EmailSignatureViewSet.partial_update` method.
    """

    user = user_with_permissions([("communication", "emailsignature")])
    email_signature = email_signature_factory(subscription=user.associated_subscription)
    data = {
        "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "image": "test.jpg",
    }

    with assertNumQueries(4):
        url = reverse("communication:email-signature-detail", kwargs={"pk": email_signature.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = EmailSignatureViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=email_signature.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_email_signature_delete(api_rf, email_signature_factory, user_with_permissions):
    """
    Testing :py:meth:`communication.views.EmailSignatureViewSet.delete` method.
    """

    user = user_with_permissions([("communication", "emailsignature")])
    email_signature = email_signature_factory(subscription=user.associated_subscription)

    with assertNumQueries(6):
        url = reverse("communication:email-signature-detail", kwargs={"pk": email_signature.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = EmailSignatureViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=email_signature.id)

    assert response.status_code == 204

    assert EmailSignature.objects.count() == 0


@pytest.mark.django_db
def test_my_email_signature_list(api_rf, user_with_permissions, email_signature_factory):
    """
    Testing :py:meth:`communication.views.MyEmailSignatureViewSet.list` method.
    """
    user = user_with_permissions([("communication", "emailsignature")])

    instance_1 = email_signature_factory(created_by=user, subscription=user.associated_subscription)
    instance_2 = email_signature_factory(created_by=user, subscription=user.associated_subscription)
    instance_3 = email_signature_factory(created_by=user, subscription=user.associated_subscription)
    email_signature_factory()

    email_signatures = [instance_1.id, instance_2.id, instance_3.id]
    index_result = [2, 1, 0]

    with assertNumQueries(3):
        url = reverse("communication:my-email-signature-list")
        request = api_rf.get(url, {}, format="json")
        request.user = user
        view = MyEmailSignatureViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [email_signatures[i] for i in index_result]
