import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from communication.models import Email
from communication.views import EmailViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 22),
        ({"search": "Fly heavy great"}, [0], 12),
        ({"search": "Edge husband seek better"}, [1], 12),
        ({"ordering": "subject"}, [0, 2, 1], 22),
        ({"ordering": "-subject"}, [1, 2, 0], 22),
        ({"ordering": "body"}, [2, 1, 0], 22),
        ({"ordering": "-body"}, [0, 1, 2], 22),
        ({"ordering": "pk"}, [0, 1, 2], 22),
        ({"ordering": "-pk"}, [2, 1, 0], 22),
        ({"ordering": "created_at"}, [0, 1, 2], 22),
        ({"ordering": "-created_at"}, [2, 1, 0], 22),
        ({"vendors": [0]}, [0], 13),
    ),
)
@pytest.mark.django_db
def test_email_list(
    api_rf,
    user_with_permissions,
    email_factory,
    vendor_factory,
    query_params,
    index_result,
    num_queries,
):
    """
    Testing :py:meth:`communication.views.EmailViewSet.list` method.
    """
    user = user_with_permissions([("communication", "email")])

    vendor_1 = vendor_factory(personal_emails=["jessica50@example.com"])
    vendor_2 = vendor_factory(business_emails=["nathan90@example.com"])

    vendors = [vendor_1, vendor_2]

    instance_1 = email_factory(
        subject="Fly heavy great work.",
        body="Forward face stage read everyone itself admit ahead",
        vendors=[vendor_1],
        subscription=user.associated_subscription,
    )
    instance_2 = email_factory(
        subject="Some mother democratic institution several interview",
        body="Edge husband seek better. Enter yeah huge.",
        vendors=[vendor_2],
        subscription=user.associated_subscription,
    )
    instance_3 = email_factory(
        subject="Memory will case four.",
        body="Cost democratic or occur writer half",
        subscription=user.associated_subscription,
    )
    email_factory()

    emails = [instance_1.id, instance_2.id, instance_3.id]
    vendors = [vendor_1.id, vendor_2.id]

    with assertNumQueries(num_queries):
        if "vendors" in query_params:
            query_params["vendors"] = [vendors[i] for i in query_params["vendors"]]

        url = reverse("communication:email-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = EmailViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [emails[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "recipient_type": ["This field is required."],
                "subject": ["This field is required."],
                "body": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "recipient_type": "INDIVIDUAL",
                "individual_recipient_type": "VENDOR",
                "tenants": [],
                "owners": [],
                "vendors": [100],
                "units": [],
                "subject": "James Ramirez",
                "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "signature": 100,
                "attachments": [],
            },
            None,
            201,
            24,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_email_create(
    api_rf,
    vendor_factory,
    email_signature_factory,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`communication.views.Email.create` method.
    """

    user = user_with_permissions([("communication", "email")])
    vendor_factory(id=100)
    email_signature_factory(id=100)

    with assertNumQueries(num_queries):
        url = reverse("communication:email-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = EmailViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert Email.objects.count() == obj_count


@pytest.mark.django_db
def test_email_retrieve(api_rf, email_factory, user_with_permissions):
    """
    Testing :py:meth:`communication.views.EmailViewSet.retrieve` method.
    """

    user = user_with_permissions([("communication", "email")])
    email = email_factory(subscription=user.associated_subscription)

    with assertNumQueries(12):
        url = reverse("communication:email-detail", kwargs={"pk": email.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = EmailViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=email.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "recipient_type",
        "individual_recipient_type",
        "tenants",
        "owners",
        "vendors",
        "units",
        "recipient_emails",
        "template",
        "subject",
        "body",
        "signature",
        "attachments",
        "created_at",
        "created_by",
    }
