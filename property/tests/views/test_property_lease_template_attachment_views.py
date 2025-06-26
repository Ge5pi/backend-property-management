import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from property.models import PropertyLeaseTemplateAttachment
from property.views import PropertyLeaseTemplateAttachmentViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"parent_property": 1}, [1, 0], 4),
    ),
)
@pytest.mark.django_db
def test_property_lease_template_attachment_list(
    api_rf,
    query_params,
    index_result,
    num_queries,
    user_with_permissions,
    property_lease_template_attachment_factory,
    property_factory,
):
    """
    Testing :py:meth:`property.views.PropertyLeaseTemplateAttachmentListAPIView` method.
    """
    user = user_with_permissions([("property", "propertyleasetemplateattachment")])
    prop = property_factory(subscription=user.associated_subscription)

    if "parent_property" in query_params:
        query_params["parent_property"] = prop.id

    instance_1 = property_lease_template_attachment_factory(
        parent_property=prop, subscription=user.associated_subscription
    )
    instance_2 = property_lease_template_attachment_factory(
        parent_property=prop, subscription=user.associated_subscription
    )
    instance_3 = property_lease_template_attachment_factory(subscription=user.associated_subscription)
    property_lease_template_attachment_factory()

    property_lease_template_attachments = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("property:property_lease_template_attachments-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = PropertyLeaseTemplateAttachmentViewSet.as_view({"get": "list"})
        response = view(request, property_id=prop.id)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [property_lease_template_attachments[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "parent_property": ["This field is required."],
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
def test_property_lease_template_attachment_create(
    api_rf,
    property_factory,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`property.views.PropertyLeaseTemplateAttachmentViewSet.create` method.
    """

    user = user_with_permissions([("property", "propertyleasetemplateattachment")])
    prop = property_factory(subscription=user.associated_subscription)

    if status_code == 201:
        data["parent_property"] = prop.id

    with assertNumQueries(num_queries):
        url = reverse("property:property_lease_template_attachments-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = PropertyLeaseTemplateAttachmentViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert PropertyLeaseTemplateAttachment.objects.count() == obj_count


@pytest.mark.django_db
def test_property_lease_template_attachment_retrieve(
    api_rf, property_lease_template_attachment_factory, user_with_permissions
):
    """
    Testing :py:meth:`property.views.PropertyLeaseTemplateAttachmentViewSet.retrieve` method.
    """

    user = user_with_permissions([("property", "propertyleasetemplateattachment")])
    property_lease_template_attachment = property_lease_template_attachment_factory(
        subscription=user.associated_subscription
    )

    with assertNumQueries(3):
        url = reverse(
            "property:property_lease_template_attachments-detail",
            kwargs={"pk": property_lease_template_attachment.id},
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = PropertyLeaseTemplateAttachmentViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=property_lease_template_attachment.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "name",
        "created_by",
        "file",
        "parent_property",
        "file_type",
        "updated_at",
    }


@pytest.mark.django_db
def test_property_lease_template_attachment_update(
    api_rf, property_lease_template_attachment_factory, user_with_permissions, property_factory
):
    """
    Testing :py:meth:`property.views.PropertyLeaseTemplateAttachmentViewSet.partial_update` method.
    """

    user = user_with_permissions([("property", "propertyleasetemplateattachment")])
    prop = property_factory(subscription=user.associated_subscription)
    property_lease_template_attachment = property_lease_template_attachment_factory(
        subscription=user.associated_subscription
    )
    data = {
        "parent_property": prop.id,
        "file": "Agreement.pdf",
        "name": "Agreement",
        "file_type": "pdf",
    }

    with assertNumQueries(5):
        url = reverse(
            "property:property_lease_template_attachments-detail",
            kwargs={"pk": property_lease_template_attachment.id},
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = PropertyLeaseTemplateAttachmentViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=property_lease_template_attachment.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_property_lease_template_attachment_delete(
    api_rf, property_lease_template_attachment_factory, user_with_permissions
):
    """
    Testing :py:meth:`property.views.PropertyLeaseTemplateAttachmentViewSet.delete` method.
    """

    user = user_with_permissions([("property", "propertyleasetemplateattachment")])
    property_lease_template_attachment = property_lease_template_attachment_factory(
        subscription=user.associated_subscription
    )

    with assertNumQueries(4):
        url = reverse(
            "property:property_lease_template_attachments-detail",
            kwargs={"pk": property_lease_template_attachment.id},
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = PropertyLeaseTemplateAttachmentViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=property_lease_template_attachment.id)

    assert response.status_code == 204

    assert PropertyLeaseTemplateAttachment.objects.count() == 0
