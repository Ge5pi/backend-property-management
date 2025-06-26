import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from communication.models import EmailTemplate
from communication.views import EmailTemplateViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 25),
        ({"search": "Fly heavy great"}, [0], 13),
        ({"search": "Edge husband seek better"}, [1], 13),
        ({"search": "jessica50@example.com"}, [0], 13),
        ({"search": "nathan90@example.com"}, [1], 13),
        ({"ordering": "subject"}, [0, 2, 1], 25),
        ({"ordering": "-subject"}, [1, 2, 0], 25),
        ({"ordering": "body"}, [2, 1, 0], 25),
        ({"ordering": "-body"}, [0, 1, 2], 25),
        ({"ordering": "pk"}, [0, 1, 2], 25),
        ({"ordering": "-pk"}, [2, 1, 0], 25),
    ),
)
@pytest.mark.django_db
def test_email_template_list(
    api_rf,
    user_with_permissions,
    email_template_factory,
    vendor_factory,
    query_params,
    index_result,
    num_queries,
):
    """
    Testing :py:meth:`communication.views.EmailTemplateViewSet.list` method.
    """
    user = user_with_permissions([("communication", "emailtemplate")])

    vendor_1 = vendor_factory(personal_emails=["jessica50@example.com"])
    vendor_2 = vendor_factory(business_emails=["nathan90@example.com"])

    instance_1 = email_template_factory(
        subject="Fly heavy great work.",
        body="Forward face stage read everyone itself admit ahead",
        vendors=[vendor_1],
        subscription=user.associated_subscription,
    )
    instance_2 = email_template_factory(
        subject="Some mother democratic institution several interview",
        body="Edge husband seek better. Enter yeah huge.",
        vendors=[vendor_2],
        subscription=user.associated_subscription,
    )
    instance_3 = email_template_factory(
        subject="Memory will case four.",
        body="Cost democratic or occur writer half",
        subscription=user.associated_subscription,
    )
    email_template_factory()

    email_templates = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("communication:email-template-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = EmailTemplateViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [email_templates[i] for i in index_result]


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
            },
            None,
            201,
            20,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_email_template_create(
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
    Testing :py:meth:`communication.views.EmailTemplate.create` method.
    """

    user = user_with_permissions([("communication", "emailtemplate")])
    vendor_factory(id=100)
    email_signature_factory(id=100)

    with assertNumQueries(num_queries):
        url = reverse("communication:email-template-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = EmailTemplateViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert EmailTemplate.objects.count() == obj_count


@pytest.mark.django_db
def test_email_template_retrieve(api_rf, email_template_factory, user_with_permissions):
    """
    Testing :py:meth:`communication.views.EmailTemplateViewSet.retrieve` method.
    """

    user = user_with_permissions([("communication", "emailtemplate")])
    email_template = email_template_factory(subscription=user.associated_subscription)

    with assertNumQueries(13):
        url = reverse("communication:email-template-detail", kwargs={"pk": email_template.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = EmailTemplateViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=email_template.id)

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
        "subject",
        "body",
        "signature",
        "created_at",
        "created_by",
    }


@pytest.mark.django_db
def test_email_template_update(
    api_rf,
    email_template_factory,
    user_with_permissions,
    email_signature_factory,
    vendor_factory,
):
    """
    Testing :py:meth:`communication.views.EmailTemplateViewSet.partial_update` method.
    """

    user = user_with_permissions([("communication", "emailtemplate")])
    email_template = email_template_factory(subscription=user.associated_subscription)
    vendor = vendor_factory()
    email_signature = email_signature_factory()
    data = {
        "recipient_type": "INDIVIDUAL",
        "individual_recipient_type": "VENDOR",
        "tenants": [],
        "owners": [],
        "vendors": [vendor.id],
        "units": [],
        "subject": "James Ramirez",
        "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "signature": email_signature.id,
    }

    with assertNumQueries(25):
        url = reverse("communication:email-template-detail", kwargs={"pk": email_template.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = EmailTemplateViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=email_template.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_email_template_delete(api_rf, email_template_factory, user_with_permissions):
    """
    Testing :py:meth:`communication.views.EmailTemplateViewSet.delete` method.
    """

    user = user_with_permissions([("communication", "emailtemplate")])
    email_template = email_template_factory(subscription=user.associated_subscription)

    with assertNumQueries(13):
        url = reverse("communication:email-template-detail", kwargs={"pk": email_template.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = EmailTemplateViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=email_template.id)

    assert response.status_code == 204

    assert EmailTemplate.objects.count() == 0
