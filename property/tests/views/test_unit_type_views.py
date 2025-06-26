import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from property.models import UnitType
from property.views import UnitTypeViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 19),
        ({"parent_property": True}, [2], 10),
    ),
)
@pytest.mark.django_db
def test_unit_list(
    api_rf, user_with_permissions, property_factory, unit_type_factory, query_params, index_result, num_queries
):
    """
    Testing :py:meth:`property.views.UnitTypeViewSet.list` method.
    """
    user = user_with_permissions([("property", "unittype")])
    prop = property_factory(subscription=user.associated_subscription)

    instance_1 = unit_type_factory(subscription=user.associated_subscription)
    instance_2 = unit_type_factory(subscription=user.associated_subscription)
    instance_3 = unit_type_factory(subscription=user.associated_subscription, parent_property=prop)
    unit_type_factory()

    if query_params.get("parent_property"):
        query_params["parent_property"] = prop.id

    unit_types = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("property:unit_type-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = UnitTypeViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [unit_types[i] for i in index_result]


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "parent_property": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "name": "name",
                "bed_rooms": 1,
                "bath_rooms": 1,
                "square_feet": 1,
                "market_rent": 1,
                "effective_date": "2021-01-01",
                "application_fee": 1,
                "tags": [],
                "estimate_turn_over_cost": 1,
                "is_cat_allowed": True,
                "is_dog_allowed": True,
                "is_smoking_allowed": True,
                "marketing_title": "marketing_title",
                "marketing_description": "marketing_description",
                "parent_property": 1,
            },
            None,
            201,
            10,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_unit_type_create(
    api_rf, property_factory, user_with_permissions, data, expected_response, status_code, num_queries, obj_count
):
    """
    Testing :py:meth:`property.views.UnitTypeViewSet.create` method.
    """

    user = user_with_permissions([("property", "unittype")])

    if status_code == 201:
        data["parent_property"] = property_factory().id

    with assertNumQueries(num_queries):
        url = reverse("property:unit_type-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = UnitTypeViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert UnitType.objects.count() == obj_count


@pytest.mark.django_db
def test_unit_type_retrieve(api_rf, unit_type_factory, user_with_permissions):
    """
    Testing :py:meth:`property.views.UnitTypeViewSet.retrieve` method.
    """

    user = user_with_permissions([("property", "unittype")])
    unit_type = unit_type_factory(subscription=user.associated_subscription)

    with assertNumQueries(9):
        url = reverse("property:unit_type-detail", kwargs={"pk": unit_type.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = UnitTypeViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=unit_type.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "name",
        "bed_rooms",
        "bath_rooms",
        "square_feet",
        "market_rent",
        "future_market_rent",
        "effective_date",
        "application_fee",
        "tags",
        "estimate_turn_over_cost",
        "is_cat_allowed",
        "is_dog_allowed",
        "is_smoking_allowed",
        "marketing_title",
        "marketing_description",
        "marketing_youtube_url",
        "parent_property",
        "cover_picture",
        "cover_picture_id",
    }


@pytest.mark.django_db
def test_unit_type_update(api_rf, unit_type_factory, user_with_permissions):
    """
    Testing :py:meth:`property.views.UnitTypeViewSet.partial_update` method.
    """

    user = user_with_permissions([("property", "unittype")])
    unit_type = unit_type_factory(subscription=user.associated_subscription)
    data = {
        "name": "name",
        "bed_rooms": 1,
        "bath_rooms": 1,
        "square_feet": 1,
        "market_rent": "1.00",
        "effective_date": "2021-01-01",
        "application_fee": "1.00",
        "tags": [],
        "estimate_turn_over_cost": "1.00",
        "is_cat_allowed": True,
        "is_dog_allowed": True,
        "is_smoking_allowed": True,
        "marketing_title": "marketing_title",
        "marketing_description": "marketing_description",
        "parent_property": unit_type.parent_property.id,
    }

    with assertNumQueries(12):
        url = reverse("property:unit_type-detail", kwargs={"pk": unit_type.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = UnitTypeViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=unit_type.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_unit_type_delete(api_rf, unit_type_factory, user_with_permissions):
    """
    Testing :py:meth:`property.views.UnitTypeViewSet.delete` method.
    """

    user = user_with_permissions([("property", "unittype")])
    unit_type = unit_type_factory(subscription=user.associated_subscription)

    with assertNumQueries(8):
        url = reverse("property:unit_type-detail", kwargs={"pk": unit_type.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = UnitTypeViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=unit_type.id)

    assert response.status_code == 204

    assert UnitType.objects.count() == 0
