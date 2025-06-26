import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from property.models import PropertyPhoto
from property.views import PropertyPhotoViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"parent_property": 1}, [1, 0], 4),
    ),
)
@pytest.mark.django_db
def test_property_photo_list(
    api_rf,
    query_params,
    index_result,
    num_queries,
    user_with_permissions,
    property_photo_factory,
    property_factory,
):
    """
    Testing :py:meth:`property.views.PropertyPhotoListAPIView` method.
    """
    user = user_with_permissions([("property", "propertyphoto")])
    prop = property_factory(subscription=user.associated_subscription)

    if "parent_property" in query_params:
        query_params["parent_property"] = prop.id

    instance_1 = property_photo_factory(parent_property=prop, subscription=user.associated_subscription)
    instance_2 = property_photo_factory(parent_property=prop, subscription=user.associated_subscription)
    instance_3 = property_photo_factory(subscription=user.associated_subscription)
    property_photo_factory()

    property_photos = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("property:property_photos-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = PropertyPhotoViewSet.as_view({"get": "list"})
        response = view(request, property_id=prop.id)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [property_photos[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "image": ["This field is required."],
                "parent_property": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "image": "image.jpg",
            },
            None,
            201,
            4,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_property_photo_create(
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
    Testing :py:meth:`property.views.PropertyPhotoViewSet.create` method.
    """

    user = user_with_permissions([("property", "propertyphoto")])
    prop = property_factory(subscription=user.associated_subscription)

    if status_code == 201:
        data["parent_property"] = prop.id

    with assertNumQueries(num_queries):
        url = reverse("property:property_photos-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = PropertyPhotoViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert PropertyPhoto.objects.count() == obj_count


@pytest.mark.django_db
def test_property_photo_retrieve(api_rf, property_photo_factory, user_with_permissions):
    """
    Testing :py:meth:`property.views.PropertyPhotoViewSet.retrieve` method.
    """

    user = user_with_permissions([("property", "propertyphoto")])
    property_photo = property_photo_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse(
            "property:property_photos-detail",
            kwargs={"pk": property_photo.id},
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = PropertyPhotoViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=property_photo.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "image",
        "is_cover",
        "parent_property",
    }


@pytest.mark.django_db
def test_property_photo_update(api_rf, property_photo_factory, user_with_permissions, property_factory):
    """
    Testing :py:meth:`property.views.PropertyPhotoViewSet.partial_update` method.
    """

    user = user_with_permissions([("property", "propertyphoto")])
    prop = property_factory(subscription=user.associated_subscription)
    property_photo = property_photo_factory(subscription=user.associated_subscription)
    data = {
        "parent_property": prop.id,
        "image": "image.png",
        "is_cover": False,
    }

    with assertNumQueries(5):
        url = reverse(
            "property:property_photos-detail",
            kwargs={"pk": property_photo.id},
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = PropertyPhotoViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=property_photo.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_property_photo_delete(api_rf, property_photo_factory, user_with_permissions):
    """
    Testing :py:meth:`property.views.PropertyPhotoViewSet.delete` method.
    """

    user = user_with_permissions([("property", "propertyphoto")])
    property_photo = property_photo_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse(
            "property:property_photos-detail",
            kwargs={"pk": property_photo.id},
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = PropertyPhotoViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=property_photo.id)

    assert response.status_code == 204

    assert PropertyPhoto.objects.count() == 0
