import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from property.models import Property
from property.views import PortfolioPropertiesListAPIView, PropertyViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (
        ({}, [2, 1, 0], 12),
        ({"search": "John Property"}, [0], 6),
        ({"search": "2370 Box 4044"}, [1], 6),
        ({"search": "Villa"}, [2], 6),
        ({"search": "prp-2"}, [1], 6),
        ({"ordering": "pk"}, [0, 1, 2], 12),
        ({"ordering": "-pk"}, [2, 1, 0], 12),
        ({"ordering": "name"}, [2, 1, 0], 12),
        ({"ordering": "-name"}, [0, 1, 2], 12),
        ({"ordering": "number_of_units"}, [0, 1, 2], 12),
        ({"ordering": "-number_of_units"}, [2, 1, 0], 12),
        ({"ordering": "owners__owner__first_name"}, [2, 1, 0], 12),
        ({"ordering": "-owners__owner__first_name"}, [0, 1, 2], 12),
        ({"property_type": True}, [2], 7),
        ({"is_occupied": True}, [2], 6),
    ),
)
@pytest.mark.django_db
def test_property_list(
    api_rf,
    user_with_permissions,
    property_factory,
    unit_type_factory,
    property_owner_factory,
    unit_factory,
    lease_factory,
    query_params,
    index_result,
    num_queries,
):
    """
    Testing :py:meth:`property.views.PropertyViewSet.list` method.
    """
    user = user_with_permissions([("property", "property")])

    instance_1 = property_factory(
        name="John Property",
        address="Unit 0472 Box 2921",
        property_type__name="Apartment",
        subscription=user.associated_subscription,
    )
    instance_2 = property_factory(
        name="Jane Property",
        address="Unit 2370 Box 4044",
        property_type__name="House",
        subscription=user.associated_subscription,
    )
    instance_3 = property_factory(
        name="Doe Property",
        address="13579 Kenneth Glens",
        property_type__name="Villa",
        subscription=user.associated_subscription,
    )
    property_factory()

    if query_params.get("search") and query_params.get("search").startswith("prp-"):
        query_params["search"] = f"prp-{instance_2.id}"

    if query_params.get("property_type"):
        query_params["property_type"] = instance_3.property_type.id

    unit_type_1 = unit_type_factory(parent_property=instance_2)
    unit_type_2 = unit_type_factory(parent_property=instance_3)
    unit_factory(unit_type=unit_type_1)
    unit_factory(unit_type=unit_type_2)
    unit = unit_factory(unit_type=unit_type_2)
    property_owner_factory(parent_property=instance_1, owner__first_name="John")
    property_owner_factory(parent_property=instance_2, owner__first_name="Jane")
    property_owner_factory(parent_property=instance_3, owner__first_name="Doe")

    lease_factory(unit=unit, status="ACTIVE", rental_application__applicant__unit=unit)

    properties = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("property:property-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = PropertyViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [properties[i] for i in index_result]
    assert response.data[0].keys() == {
        "id",
        "name",
        "property_type",
        "number_of_units",
        "is_occupied",
        "cover_picture",
        "owner_peoples",
    }


@pytest.mark.parametrize(
    "data, expected_response, status_code, num_queries, obj_count",
    (
        (
            {},
            {
                "name": ["This field is required."],
                "address": ["This field is required."],
                "property_type": ["This field is required."],
            },
            400,
            2,
            0,
        ),
        (
            {
                "name": "Property",
                "address": "123 Main St",
                "property_type": 1,
                "description": "Lorem ipsum dolor sit amet",
                "renters_tax_location_code": "123",
                "property_owner_license": "123",
                "year_built": 1977,
                "management_start_date": "1977-08-31",
                "management_end_date": "1977-08-31",
                "management_end_reason": "End of management",
                "nsf_fee": "100.00",
                "management_fees_amount": "100.00",
                "management_fees_percentage": 10,
                "management_commission_type": "percentage",
                "is_cat_allowed": True,
                "is_dog_allowed": True,
                "is_smoking_allowed": True,
                "additional_fees_gl_account": "123",
                "additional_fees_percentage": 10,
                "addition_fees_suppress": True,
                "notes": "Lorem ipsum dolor sit amet",
                "tax_authority": "IRS",
                "portfolio": "123",
                "lease_fees_amount": "100.00",
                "lease_fees_percentage": 10,
                "lease_fees_commission_type": "percentage",
                "maintenance_limit_amount": "100.00",
                "insurance_expiration_date": "1977-08-31",
                "has_home_warranty_coverage": True,
                "home_warranty_company": "Home Warranty",
                "home_warranty_expiration_date": "1977-08-31",
                "maintenance_notes": "Lorem ipsum dolor sit amet",
                "default_lease_template": 1,
                "default_lease_agenda": "Lorem ipsum dolor sit amet",
                "default_lease_renewal_template": 1,
                "default_lease_renewal_agenda": "Lorem ipsum dolor sit amet",
                "default_lease_renewal_letter_template": "Lorem ipsum dolor sit amet",
                "cover_picture": None,
                "default_renewal_terms": "monthly",
                "default_renewal_charge_by": "200.00",
                "default_renewal_additional_fee": "100.00",
                "rental_application_template": 1,
            },
            None,
            201,
            12,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_property_create(
    api_rf,
    property_type_factory,
    lease_template_factory,
    rental_application_template_factory,
    user_with_permissions,
    data,
    expected_response,
    status_code,
    num_queries,
    obj_count,
):
    """
    Testing :py:meth:`property.views.PropertyViewSet.create` method.
    """

    user = user_with_permissions([("property", "property")])

    if status_code == 201:
        data["property_type"] = property_type_factory().id
        data["default_lease_template"] = lease_template_factory().id
        data["default_lease_renewal_template"] = lease_template_factory().id
        data["rental_application_template"] = rental_application_template_factory().id

    with assertNumQueries(num_queries):
        url = reverse("property:property-list")
        request = api_rf.post(url, data, format="json")
        request.user = user
        view = PropertyViewSet.as_view({"post": "create"})
        response = view(request)

    assert response.status_code == status_code
    if expected_response:
        assert response.data == expected_response
    assert Property.objects.count() == obj_count


@pytest.mark.django_db
def test_property_retrieve(api_rf, property_factory, user_with_permissions):
    """
    Testing :py:meth:`property.views.PropertyViewSet.retrieve` method.
    """

    user = user_with_permissions([("property", "property")])
    prop = property_factory(subscription=user.associated_subscription)

    with assertNumQueries(8):
        url = reverse("property:property-detail", kwargs={"pk": prop.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = PropertyViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=prop.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "name",
        "slug",
        "address",
        "property_type",
        "description",
        "renters_tax_location_code",
        "property_owner_license",
        "year_built",
        "management_start_date",
        "management_end_date",
        "management_end_reason",
        "nsf_fee",
        "management_fees_amount",
        "management_fees_percentage",
        "management_commission_type",
        "is_cat_allowed",
        "is_dog_allowed",
        "is_smoking_allowed",
        "additional_fees_gl_account",
        "additional_fees_percentage",
        "addition_fees_suppress",
        "notes",
        "tax_authority",
        "portfolio",
        "lease_fees_amount",
        "lease_fees_percentage",
        "lease_fees_commission_type",
        "maintenance_limit_amount",
        "insurance_expiration_date",
        "has_home_warranty_coverage",
        "home_warranty_company",
        "home_warranty_expiration_date",
        "maintenance_notes",
        "default_lease_template",
        "default_lease_agenda",
        "default_lease_renewal_template",
        "default_lease_renewal_agenda",
        "default_lease_renewal_letter_template",
        "late_fee_policy",
        "cover_picture",
        "cover_picture_id",
        "default_renewal_terms",
        "default_renewal_charge_by",
        "default_renewal_additional_fee",
        "rental_application_template",
        "is_occupied",
        "is_late_fee_policy_configured",
        "number_of_units",
        "is_occupied",
        "is_late_fee_policy_configured",
        "property_type_name",
        "late_fee_base_amount",
    }


@pytest.mark.django_db
def test_property_update(api_rf, property_factory, user_with_permissions):
    """
    Testing :py:meth:`property.views.PropertyViewSet.partial_update` method.
    """

    user = user_with_permissions([("property", "property")])
    prop = property_factory(subscription=user.associated_subscription)
    data = {
        "name": "Property",
        "address": "123 Main St",
        "property_type": prop.property_type.id,
        "description": "Lorem ipsum dolor sit amet",
        "renters_tax_location_code": "123",
        "property_owner_license": "123",
        "year_built": 1977,
        "management_start_date": "1977-08-31",
        "management_end_date": "1977-08-31",
        "management_end_reason": "End of management",
        "nsf_fee": "100.00",
        "management_fees_amount": "100.00",
        "management_fees_percentage": 10,
        "management_commission_type": "percentage",
        "is_cat_allowed": True,
        "is_dog_allowed": True,
        "is_smoking_allowed": True,
        "additional_fees_gl_account": "123",
        "additional_fees_percentage": 10,
        "addition_fees_suppress": True,
        "notes": "Lorem ipsum dolor sit amet",
        "tax_authority": "IRS",
        "portfolio": "123",
        "lease_fees_amount": "100.00",
        "lease_fees_percentage": 10,
        "lease_fees_commission_type": "percentage",
        "maintenance_limit_amount": "100.00",
        "insurance_expiration_date": "1977-08-31",
        "has_home_warranty_coverage": True,
        "home_warranty_company": "Home Warranty",
        "home_warranty_expiration_date": "1977-08-31",
        "maintenance_notes": "Lorem ipsum dolor sit amet",
        "default_lease_template": prop.default_lease_template.id,
        "default_lease_agenda": "Lorem ipsum dolor sit amet",
        "default_lease_renewal_template": prop.default_lease_renewal_template.id,
        "default_lease_renewal_agenda": "Lorem ipsum dolor sit amet",
        "default_lease_renewal_letter_template": "Lorem ipsum dolor sit amet",
        "cover_picture": None,
        "default_renewal_terms": "monthly",
        "default_renewal_charge_by": "200.00",
        "default_renewal_additional_fee": "100.00",
        "rental_application_template": prop.rental_application_template.id,
    }

    with assertNumQueries(13):
        url = reverse("property:property-detail", kwargs={"pk": prop.id})
        request = api_rf.patch(url, data, format="json")
        request.user = user
        view = PropertyViewSet.as_view({"patch": "partial_update"})
        response = view(request, pk=prop.id)

    assert response.status_code == 200
    for key, value in data.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_property_delete(api_rf, property_factory, user_with_permissions):
    """
    Testing :py:meth:`property.views.PropertyViewSet.delete` method.
    """

    user = user_with_permissions([("property", "property")])
    prop = property_factory(subscription=user.associated_subscription)

    with assertNumQueries(20):
        url = reverse("property:property-detail", kwargs={"pk": prop.id})
        request = api_rf.delete(url, format="json")
        request.user = user
        view = PropertyViewSet.as_view({"delete": "destroy"})
        response = view(request, pk=prop.id)

    assert response.status_code == 204

    assert Property.objects.count() == 0


@pytest.mark.django_db
def test_portfolio_property_list(api_rf, user_with_permissions, property_factory, unit_type_factory, unit_factory):
    """
    Testing :py:meth:`property.views.PropertyViewSet.list` method.
    """
    user = user_with_permissions([("property", "property")])

    instance_1 = property_factory(subscription=user.associated_subscription)
    instance_2 = property_factory(subscription=user.associated_subscription)
    property_factory()

    unit_type_1 = unit_type_factory(parent_property=instance_1)
    unit_factory(unit_type=unit_type_1)

    properties = [instance_1.id, instance_2.id]
    index_result = [0]

    with assertNumQueries(6):
        url = reverse("property:property-list")
        request = api_rf.get(url, {}, format="json")
        request.user = user
        view = PortfolioPropertiesListAPIView.as_view()
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [properties[i] for i in index_result]
    assert response.data[0].keys() == {
        "id",
        "name",
        "cover_picture",
        "units_count",
        "occupied_units_count",
        "vacant_units_count",
        "vacant_for_days",
    }
