import pytest

from lease.models import Lease

from ..models import Tenant, Vendor, VendorType


@pytest.mark.django_db
def test_vendor_type_manager_slug_queryset(vendor_type_factory):
    """
    Testing :py:meth:`maintenance.models.VendorTypeQuerySet.annotate_slug`.
    """
    vendor_type = vendor_type_factory()
    vendor_types = VendorType.objects.annotate_slug()
    assert vendor_types.count() == 1
    assert vendor_types.get().slug == f"{VendorType.SLUG}-{vendor_type.id}"


@pytest.mark.django_db
def test_vendor_type_annotate_vendor_count_queryset(vendor_type_factory, vendor_factory):
    """
    Testing :py:meth:`maintenance.models.VendorTypeQuerySet.annotate_slug`.
    """
    vendor_type = vendor_type_factory()
    vendor_types = VendorType.objects.annotate_vendor_count()
    vendor_factory(vendor_type=vendor_type)

    assert vendor_types.count() == 1
    assert vendor_types.get().vendor_count == 1


@pytest.mark.django_db
def test_vendor_manager_slug_queryset(vendor_factory):
    """
    Testing :py:meth:`maintenance.models.VendorQuerySet.annotate_slug`.
    """
    vendor = vendor_factory()
    vendors = Vendor.objects.annotate_slug()
    assert vendors.count() == 1
    assert vendors.get().slug == f"{Vendor.SLUG}-{vendor.id}"


@pytest.mark.django_db
def test_tenant_manager_annotate_status(lease_factory):
    """
    Testing :py:meth:`maintenance.models.TenantQuerySet.annotate_status`.
    """

    lease_1 = lease_factory(status=Lease.LeaseStatus.ACTIVE)
    lease_2 = lease_factory(status=Lease.LeaseStatus.CLOSED)

    tenants = Tenant.objects.annotate_status()
    tenant_1 = tenants.get(lease=lease_1)
    tenant_2 = tenants.get(lease=lease_2)

    assert tenants.count() == 2
    assert tenant_1.status == "Current"
    assert tenant_2.status == "Past"
