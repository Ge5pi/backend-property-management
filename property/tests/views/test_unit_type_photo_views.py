import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from property.models import UnitTypePhoto
from property.views import UnitTypePhotoViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 3),
        ({"unit_type": 1}, [1, 0], 4),
    ),
)
@pytest.mark.django_db
def test_unit_type_photo_list(
    api_rf,
    query_params,
    index_result,
    num_queries,
    user_with_permissions,
    unit_type_photo_factory,
    unit_type_factory,
):
    """
    Testing :py:meth:`property.views.UnitTypePhotoListAPIView` method.
    """
    user = user_with_permissions([("property", "unittypephoto")])
    prop = unit_type_factory(subscription=user.associated_subscription)

    if "unit_type" in query_params:
        query_params["unit_type"] = prop.id

    instance_1 = unit_type_photo_factory(unit_type=prop, subscription=user.associated_subscription)
    instance_2 = unit_type_photo_factory(unit_type=prop, subscription=user.associated_subscription)
    instance_3 = unit_type_photo_factory(subscription=user.associated_subscription)
    unit_type_photo_factory()

    unit_type_photos = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("property:unit_type_photos-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = UnitTypePhotoViewSet.as_view({"get": "list"})
        response = view(request, unit_type_id=prop.id)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [unit_type_photos[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "image": ["This field is required."],
                "unit_type": ["This field is required."],
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
def test_unit_type_photo_create(
    api_rf,
    unit_type_factory,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`property.views.UnitTypePhotoViewSet.create` method.
    """

    user = user_with_permissions([("property", "unittypephoto")])
    prop = unit_type_factory(subscription=user.associated_subscription)

    if status_code == 201:
        data["unit_type"] = prop.id

    with assertNumQueries(num_queries):
        url = reverse("property:unit_type_photos-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = UnitTypePhotoViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert UnitTypePhoto.objects.count() == obj_count


@pytest.mark.django_db
def test_unit_type_photo_retrieve(api_rf, unit_type_photo_factory, user_with_permissions):
    """
    Testing :py:meth:`property.views.UnitTypePhotoViewSet.retrieve` method.
    """

    user = user_with_permissions([("property", "unittypephoto")])
    unit_type_photo = unit_type_photo_factory(subscription=user.associated_subscription)

    with assertNumQueries(3):
        url = reverse(
            "property:unit_type_photos-detail",
            kwargs={"pk": unit_type_photo.id},
        )
        request = api_rf.get(url, format="json")
        request.user = user
        view = UnitTypePhotoViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=unit_type_photo.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "image",
        "is_cover",
        "unit_type",
    }


@pytest.mark.django_db
def test_unit_type_photo_update(api_rf, unit_type_photo_factory, user_with_permissions, unit_type_factory):
    """
    Testing :py:meth:`property.views.UnitTypePhotoViewSet.partial_update` method.
    """

    user = user_with_permissions([("property", "unittypephoto")])
    prop = unit_type_factory(subscription=user.associated_subscription)
    unit_type_photo = unit_type_photo_factory(subscription=user.associated_subscription)
    data = {
        "unit_type": prop.id,
        "image": "image.png",
        "is_cover": False,
    }

    with assertNumQueries(5):
        url = reverse(
            "property:unit_type_photos-detail",
            kwargs={"pk": unit_type_photo.id},
        )
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = UnitTypePhotoViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=unit_type_photo.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_unit_type_photo_delete(api_rf, unit_type_photo_factory, user_with_permissions):
    """
    Testing :py:meth:`property.views.UnitTypePhotoViewSet.delete` method.
    """

    user = user_with_permissions([("property", "unittypephoto")])
    unit_type_photo = unit_type_photo_factory(subscription=user.associated_subscription)

    with assertNumQueries(4):
        url = reverse(
            "property:unit_type_photos-detail",
            kwargs={"pk": unit_type_photo.id},
        )
        request = api_rf.delete(url, format="json")
        request.user = user
        view = UnitTypePhotoViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=unit_type_photo.id)

    assert response.status_code == 204

    assert UnitTypePhoto.objects.count() == 0
