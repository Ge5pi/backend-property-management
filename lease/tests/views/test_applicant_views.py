import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from lease.models import Applicant
from lease.views import ApplicantViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 11),
        ({"search": "Victoria"}, [0], 7),
        ({"search": "Gutierrez"}, [1], 7),
        ({"search": "katherine18@example.com"}, [1], 7),
        ({"search": "+5802248218956"}, [1], 7),
        ({"ordering": "first_name"}, [1, 2, 0], 11),
        ({"ordering": "-first_name"}, [0, 2, 1], 11),
        ({"ordering": "last_name"}, [0, 1, 2], 11),
        ({"ordering": "-last_name"}, [2, 1, 0], 11),
        ({"ordering": "email"}, [2, 1, 0], 11),
        ({"ordering": "-email"}, [0, 1, 2], 11),
        ({"ordering": "phone_number"}, [0, 2, 1], 11),
        ({"ordering": "-phone_number"}, [1, 2, 0], 11),
        ({"ordering": "unit__name"}, [0, 1, 2], 11),
        ({"ordering": "-unit__name"}, [2, 1, 0], 11),
        ({"unit": 0}, [0], 8),
        ({"unit__parent_property": 0}, [2], 8),
        ({"rental_application__status": "DRAFT"}, [2, 1, 0], 11),
    ),
)
@pytest.mark.django_db
def test_applicant_list(
    api_rf,
    user_with_permissions,
    applicant_factory,
    query_params,
    index_result,
    num_queries,
    unit_factory,
    property_factory,
    unit_type_factory,
):
    """
    Testing :py:meth:`lease.views.ApplicantViewSet.list` method.
    """
    user = user_with_permissions([("lease", "applicant")])
    prop = property_factory()
    unit_type = unit_type_factory(parent_property=prop)
    unit_1 = unit_factory(name="Unit 1")
    unit_2 = unit_factory(name="Unit 2")
    unit_3 = unit_factory(name="Unit 3", unit_type=unit_type)

    units = [unit_1.id, unit_2.id, unit_3.id]

    if "unit" in query_params:
        query_params["unit"] = units[query_params["unit"]]

    if "unit__parent_property" in query_params:
        query_params["unit__parent_property"] = prop.id

    instance_1 = applicant_factory(
        first_name="Victoria",
        last_name="Davis",
        email="zcooper@example.org",
        phone_number="+17391924988450",
        unit=unit_1,
        subscription=user.associated_subscription,
    )
    instance_2 = applicant_factory(
        first_name="Kathleen",
        last_name="Gutierrez",
        email="katherine18@example.com",
        phone_number="+5802248218956",
        unit=unit_2,
        subscription=user.associated_subscription,
    )
    instance_3 = applicant_factory(
        first_name="Lisa",
        last_name="Morgan",
        email="alvarado@example.com",
        phone_number="+3245503475157",
        unit=unit_3,
        subscription=user.associated_subscription,
    )
    applicant_factory()

    applicants = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("lease:applicant-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = ApplicantViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [applicants[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "first_name": ["This field is required."],
                "last_name": ["This field is required."],
                "email": ["This field is required."],
                "phone_number": ["This field is required."],
                "unit": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "phone_number": "+923111234455",
                "allow_email_for_rental_application": True,
            },
            None,
            201,
            7,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_applicant_create(
    api_rf, user_with_permissions, data, expected_response, status_code, num_queries, obj_count, unit_factory
):
    """
    Testing :py:meth:`lease.views.ApplicantViewSet.create` method.
    """

    user = user_with_permissions([("lease", "applicant")])
    unit = unit_factory()

    if status_code == 201:
        data["unit"] = unit.id

    with assertNumQueries(num_queries):
        url = reverse("lease:applicant-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = ApplicantViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert Applicant.objects.count() == obj_count


@pytest.mark.django_db
def test_applicant_retrieve(api_rf, applicant_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.ApplicantViewSet.retrieve` method.
    """

    user = user_with_permissions([("lease", "applicant")])
    applicant = applicant_factory(subscription=user.associated_subscription)

    with assertNumQueries(7):
        url = reverse("lease:applicant-detail", kwargs={"pk": applicant.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = ApplicantViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=applicant.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "allow_email_for_rental_application",
        "unit",
        "rental_application",
        "status_percentage",
        "property_id",
        "property_name",
        "unit_name",
        "property_rental_application_template",
    }


@pytest.mark.django_db
def test_applicant_update(api_rf, applicant_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.ApplicantViewSet.partial_update` method.
    """
    user = user_with_permissions([("lease", "applicant")])
    applicant = applicant_factory(subscription=user.associated_subscription)
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone_number": "+923111234455",
        "allow_email_for_rental_application": True,
        "unit": applicant.unit.id,
    }

    with assertNumQueries(10):
        url = reverse("lease:applicant-detail", kwargs={"pk": applicant.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = ApplicantViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=applicant.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_applicant_delete(api_rf, applicant_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.ApplicantViewSet.delete` method.
    """

    user = user_with_permissions([("lease", "applicant")])
    applicant = applicant_factory(subscription=user.associated_subscription)

    with assertNumQueries(16):
        url = reverse("lease:applicant-detail", kwargs={"pk": applicant.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = ApplicantViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=applicant.id)

    assert response.status_code == 204

    assert Applicant.objects.count() == 0
