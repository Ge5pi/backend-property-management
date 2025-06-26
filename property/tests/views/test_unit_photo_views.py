import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from property.models import UnitPhoto
from property.views import UnitPhotoViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"unit": 1}, [1, 0], 4),
    ),
)
@pytest.mark.django_db
def test_unit_photo_list(
    api_rf,
    query_params,
    index_result,
    num_queries,
    user_with_permissions,
    unit_photo_factory,
    unit_factory,
):
    """
    Testing :py:meth:`property.views.UnitPhotoListAPIView` method.
    """
    user = user_with_permissions([("property", "unitphoto")])
    prop = unit_factory(subscription=user.associated_subscription)

    if "unit" in query_params:
        query_params["unit"] = prop.id

    instance_1 = unit_photo_factory(unit=prop, subscription=user.associated_subscription)
    instance_2 = unit_photo_factory(unit=prop, subscription=user.associated_subscription)
    instance_3 = unit_photo_factory(subscription=user.associated_subscription)
    unit_photo_factory()

    unit_photos = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("property:unit_photos-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = UnitPhotoViewSet.as_view({"get": "list"})
        response = view(request, unit_id=prop.id)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [unit_photos[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "image": ["This field is required."],
                "unit": ["This field is required."],
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
def test_unit_photo_create(
    api_rf,
    unit_factory,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`property.views.UnitPhotoViewSet.create` method.
    """

    user = user_with_permissions([("property", "unitphoto")])
    prop = unit_factory(subscription=user.associated_subscription)

    if status_code == 201:
        data["unit"] = prop.id

    with assertNumQueries(num_queries):
        url = reverse("property:unit_photos-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = UnitPhotoViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert UnitPhoto.objects.count() == obj_count


@pytest.mark.django_db
def test_unit_photo_retrieve(api_rf, unit_photo_factory, user_with_permissions):
    """
    Testing :py:meth:`property.views.UnitPhotoViewSet.retrieve` method.
    """

    user = user_with_permissions([("property", "unitphoto")])
    unit_photo = unit_photo_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse(
            "property:unit_photos-detail",
            kwargs={"pk": unit_photo.id},
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = UnitPhotoViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=unit_photo.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "image",
        "is_cover",
        "unit",
    }


@pytest.mark.django_db
def test_unit_photo_update(api_rf, unit_photo_factory, user_with_permissions, unit_factory):
    """
    Testing :py:meth:`property.views.UnitPhotoViewSet.partial_update` method.
    """

    user = user_with_permissions([("property", "unitphoto")])
    prop = unit_factory(subscription=user.associated_subscription)
    unit_photo = unit_photo_factory(subscription=user.associated_subscription)
    data = {
        "unit": prop.id,
        "image": "image.png",
        "is_cover": False,
    }

    with assertNumQueries(5):
        url = reverse(
            "property:unit_photos-detail",
            kwargs={"pk": unit_photo.id},
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = UnitPhotoViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=unit_photo.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_unit_photo_delete(api_rf, unit_photo_factory, user_with_permissions):
    """
    Testing :py:meth:`property.views.UnitPhotoViewSet.delete` method.
    """

    user = user_with_permissions([("property", "unitphoto")])
    unit_photo = unit_photo_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse(
            "property:unit_photos-detail",
            kwargs={"pk": unit_photo.id},
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = UnitPhotoViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=unit_photo.id)

    assert response.status_code == 204

    assert UnitPhoto.objects.count() == 0
