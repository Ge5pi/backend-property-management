import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from lease.models import RentalApplicationTemplate
from lease.views import RentalApplicationTemplateViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"search": "Template 2"}, [1], 3),
        ({"search": "way yourself already"}, [0], 3),
        ({"ordering": "name"}, [0, 1, 2], 3),
        ({"ordering": "-name"}, [2, 1, 0], 3),
        ({"ordering": "description"}, [2, 1, 0], 3),
        ({"ordering": "-description"}, [0, 1, 2], 3),
        ({"ordering": "created_at"}, [0, 1, 2], 3),
        ({"ordering": "-created_at"}, [2, 1, 0], 3),
    ),
)
@pytest.mark.django_db
def test_rental_application_template_list(
    api_rf, user_with_permissions, rental_application_template_factory, query_params, index_result, num_queries
):
    """
    Testing :py:meth:`lease.views.RentalApplicationTemplateViewSet.list` method.
    """
    user = user_with_permissions([("lease", "rentalapplicationtemplate")])

    instance_1 = rental_application_template_factory(
        name="Template 1",
        description="Place way yourself already particular.",
        subscription=user.associated_subscription,
    )
    instance_2 = rental_application_template_factory(
        name="Template 2",
        description="Investment hear sea want product effort hair.",
        subscription=user.associated_subscription,
    )
    instance_3 = rental_application_template_factory(
        name="Template 3", description="Foreign that morning water", subscription=user.associated_subscription
    )
    rental_application_template_factory()
    rental_application_templates = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("lease:rental-application-template-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = RentalApplicationTemplateViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [rental_application_templates[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {"name": ["This field is required."]},
            400,
            2,
            0,
        ),
        (
            {
                "name": "Rental Application Template",
                "description": "Rental Application Template Description",
                "general_info": True,
                "personal_details": True,
                "rental_history": True,
                "financial_info": True,
                "dependents_info": True,
                "other_info": True,
            },
            None,
            201,
            3,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_rental_application_template_create(
    api_rf, user_with_permissions, data, expected_response, status_code, num_queries, obj_count
):
    """
    Testing :py:meth:`lease.views.RentalApplicationTemplateViewSet.create` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationtemplate")])

    with assertNumQueries(num_queries):
        url = reverse("lease:rental-application-template-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = RentalApplicationTemplateViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert RentalApplicationTemplate.objects.count() == obj_count


@pytest.mark.django_db
def test_rental_application_template_retrieve(api_rf, rental_application_template_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.RentalApplicationTemplateViewSet.retrieve` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationtemplate")])
    rental_application_template = rental_application_template_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse("lease:rental-application-template-detail", kwargs={"pk": rental_application_template.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = RentalApplicationTemplateViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=rental_application_template.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "name",
        "description",
        "general_info",
        "personal_details",
        "rental_history",
        "financial_info",
        "dependents_info",
        "other_info",
        "created_at",
    }


@pytest.mark.django_db
def test_rental_application_template_update(api_rf, rental_application_template_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.RentalApplicationTemplateViewSet.partial_update` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationtemplate")])
    rental_application_template = rental_application_template_factory(subscription=user.associated_subscription)
    data = {
        "name": "Rental Application Template",
        "description": "Rental Application Template Description",
        "general_info": True,
        "personal_details": True,
        "rental_history": True,
        "financial_info": True,
        "dependents_info": True,
        "other_info": True,
    }

    with assertNumQueries(4):
        url = reverse("lease:rental-application-template-detail", kwargs={"pk": rental_application_template.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = RentalApplicationTemplateViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=rental_application_template.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_rental_application_template_delete(api_rf, rental_application_template_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.RentalApplicationTemplateViewSet.delete` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationtemplate")])
    rental_application_template = rental_application_template_factory(subscription=user.associated_subscription)

    with assertNumQueries(5):
        url = reverse("lease:rental-application-template-detail", kwargs={"pk": rental_application_template.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = RentalApplicationTemplateViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=rental_application_template.id)

    assert response.status_code == 204

    assert RentalApplicationTemplate.objects.count() == 0
