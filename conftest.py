import pytest
from pytest_factoryboy import register

from accounting.tests.factories import (
    AccountAttachmentFactory,
    AccountFactory,
    ChargeAttachmentFactory,
    ChargeFactory,
    GeneralLedgerAccountFactory,
    GeneralLedgerTransactionFactory,
    InvoiceFactory,
    PaymentAttachmentFactory,
    PaymentFactory,
)
from authentication.tests.factories import GroupFactory, RoleFactory, SuperUserFactory, UserFactory
from communication.tests.factories import (
    AnnouncementAttachmentFactory,
    AnnouncementFactory,
    ContactFactory,
    EmailAttachmentFactory,
    EmailFactory,
    EmailSignatureFactory,
    EmailTemplateFactory,
    NoteAttachmentFactory,
    NoteFactory,
)
from core.tests import ContentTypeFactory
from lease.tests.factories import (
    ApplicantFactory,
    LeaseFactory,
    LeaseTemplateFactory,
    RentalApplicationAdditionalIncomeFactory,
    RentalApplicationAttachmentFactory,
    RentalApplicationDependentFactory,
    RentalApplicationEmergencyContactFactory,
    RentalApplicationFactory,
    RentalApplicationFinancialInformationFactory,
    RentalApplicationPetsFactory,
    RentalApplicationResidentialHistoryFactory,
    RentalApplicationTemplateFactory,
    SecondaryTenantFactory,
)
from maintenance.tests.factories import (
    AreaFactory,
    AreaItemFactory,
    FixedAssetFactory,
    InspectionFactory,
    InventoryFactory,
    LaborFactory,
    ProjectExpenseAttachmentFactory,
    ProjectExpenseFactory,
    ProjectFactory,
    PurchaseOrderAttachmentFactory,
    PurchaseOrderFactory,
    PurchaseOrderItemFactory,
    ServiceRequestAttachmentFactory,
    ServiceRequestFactory,
    WorkOrderFactory,
)
from people.tests.factories import (
    OwnerPeopleFactory,
    OwnerUpcomingActivityFactory,
    TenantAttachmentFactory,
    TenantFactory,
    TenantUpcomingActivityFactory,
    VendorAddressFactory,
    VendorAttachmentFactory,
    VendorFactory,
    VendorTypeFactory,
)
from property.tests.factories import (
    PropertyAttachmentFactory,
    PropertyFactory,
    PropertyLateFeePolicyFactory,
    PropertyLeaseRenewalAttachmentFactory,
    PropertyLeaseTemplateAttachmentFactory,
    PropertyOwnerFactory,
    PropertyPhotoFactory,
    PropertyUpcomingActivityFactory,
    PropertyUtilityBillingFactory,
    RentableItemFactory,
    UnitFactory,
    UnitPhotoFactory,
    UnitTypeFactory,
    UnitTypePhotoFactory,
    UnitUpcomingActivityFactory,
)
from subscription.tests import SubscriptionFactory
from system_preferences.tests.factories import (
    BusinessInformationFactory,
    ContactCategoryFactory,
    InventoryItemTypeFactory,
    InventoryLocationFactory,
    LabelFactory,
    ManagementFeeFactory,
    PropertyTypeFactory,
    TagFactory,
)


@pytest.fixture
def api_client():
    """Returns a Django Rest Framework APIClient"""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def api_rf():
    """Returns a Django Rest Framework APIRequestFactory"""
    from rest_framework.test import APIRequestFactory

    return APIRequestFactory()


@pytest.fixture
def get_permissions():
    """Returns a function that allows to easily get permission objects for their app_label, model and codename.

    ``perm_list`` must be a list of tuples (app_label, model, codenames), whereas codenames is a list of permission
    names for the model.
    """

    def inner(perm_list):
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        from django.db.models import Q

        result: list[Permission] = []
        for app_label, model in perm_list:
            content_type = ContentType.objects.get(app_label=app_label, model=model)

            permission = Permission.objects.filter(Q(content_type=content_type))
            if permission.count() > 0:
                result.extend(permission.all())
        return result

    return inner


@pytest.fixture
def user_with_permissions(get_permissions, user_factory):
    """
    Generates a new user with the provided permissions. Uses the ``get_permissions`` fixture to generate the
    permissions.
    """

    def generate(permission_list, **kwargs):
        permissions = get_permissions(permission_list)
        user = user_factory(**kwargs)
        user.user_permissions.set(permissions)
        return user

    return generate


@pytest.fixture
def tenant_user_with_permissions(user_with_permissions, lease_factory):
    """
    Generates a new user with the provided permissions. Uses the ``user_with_permissions`` fixture to generate the
    user with permissions and create a tenant record.
    """

    def generate(permission_list, **kwargs) -> tuple:
        user = user_with_permissions(permission_list, **kwargs)
        lease = lease_factory(status="ACTIVE", subscription=user.associated_subscription)
        lease.primary_tenant.user = user
        lease.primary_tenant.save()
        return user, lease

    return generate


# Authentication
register(UserFactory)
register(SuperUserFactory)
register(GroupFactory)
register(RoleFactory)

# Settings
register(PropertyTypeFactory)
register(InventoryItemTypeFactory)
register(InventoryLocationFactory)
register(LabelFactory)
register(TagFactory)
register(ManagementFeeFactory)
register(BusinessInformationFactory)
register(ContactCategoryFactory)

# Maintenance
register(InventoryFactory)
register(FixedAssetFactory)
register(ServiceRequestFactory)
register(WorkOrderFactory)
register(LaborFactory)
register(InspectionFactory)
register(AreaFactory)
register(AreaItemFactory)
register(ProjectFactory)
register(PurchaseOrderFactory)
register(PurchaseOrderItemFactory)
register(PurchaseOrderAttachmentFactory)
register(ServiceRequestAttachmentFactory)
register(ProjectExpenseFactory)
register(ProjectExpenseAttachmentFactory)

# People
register(VendorTypeFactory)
register(VendorFactory)
register(VendorAddressFactory)
register(VendorAttachmentFactory)
register(TenantFactory)
register(TenantAttachmentFactory)
register(TenantUpcomingActivityFactory)
register(OwnerUpcomingActivityFactory)
register(OwnerPeopleFactory)

# Property
register(PropertyFactory)
register(PropertyAttachmentFactory)
register(PropertyPhotoFactory)
register(PropertyOwnerFactory)
register(PropertyUtilityBillingFactory)
register(PropertyLateFeePolicyFactory)
register(PropertyLeaseTemplateAttachmentFactory)
register(PropertyLeaseRenewalAttachmentFactory)
register(PropertyUpcomingActivityFactory)
register(UnitTypeFactory)
register(UnitFactory)
register(UnitUpcomingActivityFactory)
register(UnitTypePhotoFactory)
register(UnitPhotoFactory)
register(RentableItemFactory)

# Communication
register(ContactFactory)
register(NoteFactory)
register(NoteAttachmentFactory)
register(EmailSignatureFactory)
register(EmailFactory)
register(EmailTemplateFactory)
register(EmailAttachmentFactory)
register(AnnouncementFactory)
register(AnnouncementAttachmentFactory)

# Lease
register(LeaseFactory)
register(ApplicantFactory)
register(RentalApplicationFactory)
register(RentalApplicationTemplateFactory)
register(RentalApplicationEmergencyContactFactory)
register(RentalApplicationResidentialHistoryFactory)
register(RentalApplicationFinancialInformationFactory)
register(RentalApplicationAdditionalIncomeFactory)
register(RentalApplicationDependentFactory)
register(RentalApplicationPetsFactory)
register(RentalApplicationAttachmentFactory)
register(LeaseTemplateFactory)
register(SecondaryTenantFactory)

# Accounting
register(InvoiceFactory)
register(ChargeFactory)
register(ChargeAttachmentFactory)
register(AccountFactory)
register(AccountAttachmentFactory)
register(PaymentFactory)
register(PaymentAttachmentFactory)
register(GeneralLedgerAccountFactory)
register(GeneralLedgerTransactionFactory)

# Subscription
register(SubscriptionFactory)

# Core
register(ContentTypeFactory)
