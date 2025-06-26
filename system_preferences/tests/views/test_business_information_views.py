import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from system_preferences.models import BusinessInformation
from system_preferences.views import BusinessInformationViewSet


@pytest.mark.django_db
def test_business_information_list(api_rf, user_with_permissions, business_information_factory):
    """
    Testing :py:meth:`system_preferences.views.BusinessInformationViewSet.list` method.
    """
    user = user_with_permissions([("system_preferences", "businessinformation")])

    instance_1 = business_information_factory(subscription=user.associated_subscription)
    instance_2 = business_information_factory(subscription=user.associated_subscription)
    instance_3 = business_information_factory(subscription=user.associated_subscription)
    business_information_factory()

    business_info = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(3):
        url = reverse("system_preferences:business-information-list")
        request = api_rf.get(url, {}, format="json")
        request.user = user
        view = BusinessInformationViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == 3
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [business_info[i] for i in [2, 1, 0]]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "logo": ["This field is required."],
                "name": ["This field is required."],
                "description": ["This field is required."],
                "building_or_office_number": ["This field is required."],
                "street": ["This field is required."],
                "city": ["This field is required."],
                "postal_code": ["This field is required."],
                "state": ["This field is required."],
                "country": ["This field is required."],
                "primary_email": ["This field is required."],
                "phone_number": ["This field is required."],
                "tax_identity_type": ["This field is required."],
                "tax_payer_id": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "secondary_email": "john@example.io",
                "telephone_number": "+1 (202) 555-9890",
            },
            {
                "logo": ["This field is required."],
                "name": ["This field is required."],
                "description": ["This field is required."],
                "building_or_office_number": ["This field is required."],
                "street": ["This field is required."],
                "city": ["This field is required."],
                "postal_code": ["This field is required."],
                "state": ["This field is required."],
                "country": ["This field is required."],
                "primary_email": ["This field is required."],
                "phone_number": ["This field is required."],
                "tax_identity_type": ["This field is required."],
                "tax_payer_id": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "logo": "http://www.smith.com/post/",
                "name": "Angelica Morales",
                "description": "Up military ball later allow interview",
                "building_or_office_number": "357",
                "street": "66874 Willis Center Suite 209",
                "city": "Jerrytown",
                "postal_code": "94067",
                "state": "SV",
                "country": "Guinea-Bissau",
                "primary_email": "kruegerpaula@example.com",
                "secondary_email": "veronicaharrell@example.net",
                "phone_number": "+1 (202) 555-9890",
                "telephone_number": "+1 (202) 555-9921",
                "tax_identity_type": "yard",
                "tax_payer_id": "pattern",
            },
            None,
            201,
            3,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_business_information_create(
    api_rf, user_with_permissions, data, expected_response, status_code, num_queries, obj_count
):
    """
    Testing :py:meth:`system_preferences.views.BusinessInformationViewSet.create` method.
    """

    user = user_with_permissions([("system_preferences", "businessinformation")])

    with assertNumQueries(num_queries):
        url = reverse("system_preferences:business-information-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = BusinessInformationViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert BusinessInformation.objects.count() == obj_count


@pytest.mark.parametrize(
    "data",
    (
        {
            "logo": "http://www.smith.com/post/",
            "name": "Angelica Morales",
            "description": "Up military ball later allow interview",
            "building_or_office_number": "357",
            "street": "66874 Willis Center Suite 209",
            "city": "Jerrytown",
            "postal_code": "94067",
            "state": "SV",
            "country": "Guinea-Bissau",
            "primary_email": "kruegerpaula@example.com",
            "secondary_email": "veronicaharrell@example.net",
            "phone_number": "+12025559890",
            "telephone_number": "+12025559921",
            "tax_identity_type": "yard",
            "tax_payer_id": "pattern",
        },
    ),
)
@pytest.mark.django_db
def test_business_information_update(api_rf, business_information_factory, user_with_permissions, data):
    """
    Testing :py:meth:`system_preferences.views.BusinessInformationViewSet.partial_update` method.
    """

    user = user_with_permissions([("system_preferences", "businessinformation")])
    business_information = business_information_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse(
            "system_preferences:business-information-detail",
            kwargs={"pk": business_information.id},
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = BusinessInformationViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=business_information.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value
