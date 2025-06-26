import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from lease.models import LeaseTemplate
from lease.views import LeaseTemplateViewSet


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
def test_lease_template_list(
    api_rf, user_with_permissions, lease_template_factory, query_params, index_result, num_queries
):
    """
    Testing :py:meth:`lease.views.LeaseTemplateViewSet.list` method.
    """
    user = user_with_permissions([("lease", "leasetemplate")])

    instance_1 = lease_template_factory(
        name="Template 1",
        description="Place way yourself already particular.",
        subscription=user.associated_subscription,
    )
    instance_2 = lease_template_factory(
        name="Template 2",
        description="Investment hear sea want product effort hair.",
        subscription=user.associated_subscription,
    )
    instance_3 = lease_template_factory(
        name="Template 3", description="Foreign that morning water", subscription=user.associated_subscription
    )
    lease_template_factory()

    lease_templates = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("lease:lease-template-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = LeaseTemplateViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [lease_templates[i] for i in index_result]


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
                "name": "Test Name",
                "description": "Test Description",
                "rules_and_policies": ["Test Rules"],
                "condition_of_premises": ["Test Conditions"],
                "right_of_inspection": True,
                "conditions_of_moving_out": ["Test Conditions"],
                "releasing_policies": ["Test Policies"],
                "final_statement": "Test Statement",
            },
            None,
            201,
            3,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_lease_template_create(
    api_rf, user_with_permissions, data, expected_response, status_code, num_queries, obj_count
):
    """
    Testing :py:meth:`lease.views.LeaseTemplateViewSet.create` method.
    """

    user = user_with_permissions([("lease", "leasetemplate")])

    with assertNumQueries(num_queries):
        url = reverse("lease:lease-template-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = LeaseTemplateViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert LeaseTemplate.objects.count() == obj_count


@pytest.mark.django_db
def test_lease_template_retrieve(api_rf, lease_template_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.LeaseTemplateViewSet.retrieve` method.
    """

    user = user_with_permissions([("lease", "leasetemplate")])
    lease_template = lease_template_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse("lease:lease-template-detail", kwargs={"pk": lease_template.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = LeaseTemplateViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=lease_template.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "name",
        "description",
        "rules_and_policies",
        "condition_of_premises",
        "right_of_inspection",
        "conditions_of_moving_out",
        "releasing_policies",
        "final_statement",
        "created_at",
    }


@pytest.mark.django_db
def test_lease_template_update(api_rf, lease_template_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.LeaseTemplateViewSet.partial_update` method.
    """

    user = user_with_permissions([("lease", "leasetemplate")])
    lease_template = lease_template_factory(subscription=user.associated_subscription)
    data = {
        "name": "Test Name",
        "description": "Test Description",
        "rules_and_policies": ["Test Rules"],
        "condition_of_premises": ["Test Conditions"],
        "right_of_inspection": True,
        "conditions_of_moving_out": ["Test Conditions"],
        "releasing_policies": ["Test Policies"],
        "final_statement": "Test Statement",
    }

    with assertNumQueries(4):
        url = reverse("lease:lease-template-detail", kwargs={"pk": lease_template.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = LeaseTemplateViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=lease_template.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_lease_template_delete(api_rf, lease_template_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.LeaseTemplateViewSet.delete` method.
    """

    user = user_with_permissions([("lease", "leasetemplate")])
    lease_template = lease_template_factory(subscription=user.associated_subscription)

    with assertNumQueries(7):
        url = reverse("lease:lease-template-detail", kwargs={"pk": lease_template.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = LeaseTemplateViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=lease_template.id)

    assert response.status_code == 204

    assert LeaseTemplate.objects.count() == 0
