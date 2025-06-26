import pytest
from django.utils import timezone

from property.models import Property, PropertyLateFeePolicy, Unit, UnitType


@pytest.mark.django_db
def test_property_manager_slug_queryset(property_factory):
    """
    Testing :py:meth:`property.managers.PropertyQuerySet.annotate_slug`.
    """
    prop = property_factory()
    props = Property.objects.annotate_slug()  # type: ignore[attr-defined]
    assert props.count() == 1
    assert props.get().slug == f"{Property.SLUG}-{prop.id}"


@pytest.mark.django_db
def test_property_manager_annotate_data(
    property_factory, unit_type_factory, unit_factory, lease_factory, applicant_factory, rental_application_factory
):
    """
    Testing :py:meth:`property.managers.PropertyQuerySet.annotate_data`.
    """
    prop = property_factory()
    unit_type = unit_type_factory(parent_property=prop)
    unit = unit_factory(unit_type=unit_type)
    prop = Property.objects.annotate_data().get(id=prop.id)

    assert prop.number_of_units == 1
    assert not prop.is_occupied
    assert not prop.is_late_fee_policy_configured

    applicant = applicant_factory(first_name="John", last_name="Doe", unit=unit)
    rental_application = rental_application_factory(applicant=applicant)
    lease_factory(rental_application=rental_application, unit=unit, status="ACTIVE")
    prop = Property.objects.annotate_data().get(id=prop.id)

    assert prop.is_occupied

    prop.late_fee_policy.late_fee_type = "flat"
    prop.late_fee_policy.eligible_charges = 100
    prop.late_fee_policy.save()
    prop = Property.objects.annotate_data().get(id=prop.id)

    assert prop.is_late_fee_policy_configured


@pytest.mark.django_db
def test_property_manager_annotate_portfolio_data(
    property_factory, unit_type_factory, unit_factory, lease_factory, applicant_factory, rental_application_factory
):
    """
    Testing :py:meth:`property.managers.PropertyQuerySet.annotate_portfolio_data`.
    """
    prop = property_factory()
    unit_type = unit_type_factory(parent_property=prop)
    unit = unit_factory(unit_type=unit_type)
    prop = Property.objects.annotate_portfolio_data().get(id=prop.id)

    assert prop.units_count == 1
    assert prop.occupied_units_count == 0
    assert prop.vacant_units_count == 1

    applicant = applicant_factory(first_name="John", last_name="Doe", unit=unit)
    rental_application = rental_application_factory(applicant=applicant)
    lease_factory(rental_application=rental_application, unit=unit, status="ACTIVE")
    prop = Property.objects.annotate_portfolio_data().get(id=prop.id)

    assert prop.occupied_units_count == 1
    assert prop.vacant_units_count == 0


@pytest.mark.django_db
def test_late_fee_policy_manager_annotate_is_expired(property_factory):
    """
    Testing :py:meth:`property.managers.LateFeePolicyQuerySet.annotate_is_expired`.
    """

    prop = property_factory()
    prop.late_fee_policy.start_date = timezone.now() - timezone.timedelta(days=1)
    prop.late_fee_policy.end_date = timezone.now() + timezone.timedelta(days=1)
    prop.late_fee_policy.save()
    late_fee_policy = prop.late_fee_policy
    late_fee_policy = PropertyLateFeePolicy.objects.annotate_is_expired().get(id=late_fee_policy.id)

    assert not late_fee_policy.is_expired

    late_fee_policy.end_date = timezone.now() - timezone.timedelta(days=1)
    late_fee_policy.save()
    late_fee_policy = PropertyLateFeePolicy.objects.annotate_is_expired().get(id=late_fee_policy.id)

    assert late_fee_policy.is_expired


@pytest.mark.django_db
def test_unit_type_apply_on_all_units(unit_type_factory, unit_factory):
    """
    Testing :py:meth:`property.managers.UnitTypeManager.apply_on_all_units`.
    """
    unit_type = unit_type_factory()
    unit_1 = unit_factory(unit_type=unit_type)
    unit_2 = unit_factory(unit_type=unit_type)
    unit_3 = unit_factory(unit_type=unit_type)

    UnitType.objects.apply_on_all_units(unit_type)

    assert unit_1.market_rent == unit_type.market_rent
    assert unit_1.future_market_rent == unit_type.future_market_rent
    assert unit_1.effective_date == unit_type.effective_date
    assert unit_1.application_fee == unit_type.application_fee
    assert unit_1.estimate_turn_over_cost == unit_type.estimate_turn_over_cost

    assert unit_2.market_rent == unit_type.market_rent
    assert unit_2.future_market_rent == unit_type.future_market_rent
    assert unit_2.effective_date == unit_type.effective_date
    assert unit_2.application_fee == unit_type.application_fee
    assert unit_2.estimate_turn_over_cost == unit_type.estimate_turn_over_cost

    assert unit_3.market_rent == unit_type.market_rent
    assert unit_3.future_market_rent == unit_type.future_market_rent
    assert unit_3.effective_date == unit_type.effective_date
    assert unit_3.application_fee == unit_type.application_fee
    assert unit_3.estimate_turn_over_cost == unit_type.estimate_turn_over_cost


@pytest.mark.django_db
def test_unit_manager_slug_queryset(unit_factory):
    """
    Testing :py:meth:`property.managers.UnitQuerySet.annotate_slug`.
    """
    unit = unit_factory()
    units = Unit.objects.annotate_slug()  # type: ignore[attr-defined]
    assert units.count() == 1
    assert units.get().slug == f"{Unit.SLUG}-{unit.id}"


@pytest.mark.django_db
def test_unit_annotate_data(unit_factory, lease_factory, freezer):
    """
    Testing :py:meth:`property.managers.UnitQuerySet.annotate_data`.
    """
    freezer.move_to("2023-01-01 00:00:00")
    unit = unit_factory()

    freezer.move_to("2023-03-01 00:00:00")
    unit = Unit.objects.annotate_data().get(id=unit.id)
    assert unit.vacant_for_days == (timezone.now() - unit.created_at).days

    lease = lease_factory(rental_application__applicant__unit=unit, unit=unit, status="ACTIVE")
    unit = Unit.objects.annotate_data().get(id=unit.id)

    assert unit.is_occupied
    assert unit.lease_id == lease.id
    assert unit.tenant_id == lease.primary_tenant.id
    assert unit.tenant_first_name == lease.primary_tenant.first_name
    assert unit.tenant_last_name == lease.primary_tenant.last_name

    lease.status = "CLOSED"
    lease.end_date = timezone.now() - timezone.timedelta(days=1)
    lease.save()
    unit = Unit.objects.annotate_data().get(id=unit.id)

    assert unit.vacant_for_days == 1
