import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from lease.models import RentalApplicationAttachment
from lease.views import RentalApplicationAttachmentViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"rental_application": 0}, [0], 4),
    ),
)
@pytest.mark.django_db
def test_rental_application_attachment_list(
    api_rf,
    user_with_permissions,
    rental_application_attachment_factory,
    query_params,
    index_result,
    num_queries,
    rental_application_factory,
):
    """
    Testing :py:meth:`lease.views.RentalApplicationAttachmentViewSet.list` method.
    """
    user = user_with_permissions([("lease", "rentalapplicationattachment")])
    rental_application = rental_application_factory()
    rental_applications = [rental_application.id]
    if "rental_application" in query_params:
        query_params["rental_application"] = rental_applications[query_params["rental_application"]]

    instance_1 = rental_application_attachment_factory(
        rental_application=rental_application, subscription=user.associated_subscription
    )
    instance_2 = rental_application_attachment_factory(subscription=user.associated_subscription)
    instance_3 = rental_application_attachment_factory(subscription=user.associated_subscription)
    rental_application_attachment_factory()

    rental_application_attachments = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("lease:rental-application-attachment-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = RentalApplicationAttachmentViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [rental_application_attachments[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "file": ["This field is required."],
                "file_type": ["This field is required."],
                "rental_application": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "name": "Test Name",
                "file": "Test File",
                "file_type": "image/jpeg",
            },
            None,
            201,
            8,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_rental_application_attachment_create(
    api_rf,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
    rental_application_factory,
):
    """
    Testing :py:meth:`lease.views.RentalApplicationAttachmentViewSet.create` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationattachment")])
    rental_application = rental_application_factory()
    if status_code == 201:
        data["rental_application"] = rental_application.id

    with assertNumQueries(num_queries):
        url = reverse("lease:rental-application-attachment-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = RentalApplicationAttachmentViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert RentalApplicationAttachment.objects.count() == obj_count


@pytest.mark.django_db
def test_rental_application_attachment_retrieve(api_rf, rental_application_attachment_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.RentalApplicationAttachmentViewSet.retrieve` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationattachment")])
    rental_application_attachment = rental_application_attachment_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse(
            "lease:rental-application-attachment-detail",
            kwargs={"pk": rental_application_attachment.id},
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = RentalApplicationAttachmentViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=rental_application_attachment.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "name",
        "created_by",
        "file",
        "rental_application",
        "file_type",
        "updated_at",
    }


@pytest.mark.django_db
def test_rental_application_attachment_update(api_rf, rental_application_attachment_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.RentalApplicationAttachmentViewSet.partial_update` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationattachment")])
    rental_application_attachment = rental_application_attachment_factory(subscription=user.associated_subscription)
    data = {
        "name": "Test Name",
        "file": "Test File",
        "rental_application": rental_application_attachment.rental_application.id,
        "file_type": "image/jpeg",
    }

    with assertNumQueries(5):
        url = reverse(
            "lease:rental-application-attachment-detail",
            kwargs={"pk": rental_application_attachment.id},
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = RentalApplicationAttachmentViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=rental_application_attachment.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_rental_application_attachment_delete(api_rf, rental_application_attachment_factory, user_with_permissions):
    """
    Testing :py:meth:`lease.views.RentalApplicationAttachmentViewSet.delete` method.
    """

    user = user_with_permissions([("lease", "rentalapplicationattachment")])
    rental_application_attachment = rental_application_attachment_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse(
            "lease:rental-application-attachment-detail",
            kwargs={"pk": rental_application_attachment.id},
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = RentalApplicationAttachmentViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=rental_application_attachment.id)

    assert response.status_code == 204

    assert RentalApplicationAttachment.objects.count() == 0
