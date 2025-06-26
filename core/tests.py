import factory  # type: ignore[import]
import pytest
from django.core import management
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from .models import BaseAttachment, SubscriptionAbstractModel, UpcomingActivityAbstract
from .views import ModelChoicesListAPIView


class SubscriptionAbstractFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SubscriptionAbstractModel
        abstract = True

    subscription = factory.SubFactory("subscription.tests.SubscriptionFactory")


class UpcomingActivityAbstractFactory(SubscriptionAbstractFactory):
    class Meta:
        model = UpcomingActivityAbstract
        abstract = True

    title = factory.Sequence(lambda n: "Task #%d" % n)
    description = factory.Faker("text")
    date = factory.Faker("date")
    start_time = factory.Faker("time")
    end_time = factory.Faker("time")
    label = factory.SubFactory("system_preferences.tests.factories.LabelFactory")
    assign_to = factory.SubFactory("authentication.tests.factories.UserFactory")
    status = factory.Faker("boolean")


class BaseAttachmentFactory(SubscriptionAbstractFactory):
    class Meta:
        model = BaseAttachment
        abstract = True

    name = factory.Faker("text", max_nb_chars=30)
    file = factory.Faker("file_name")
    file_type = factory.Faker("file_extension")


class ContentTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "contenttypes.ContentType"

    app_label = "core"
    model = factory.Faker("word")


@pytest.mark.order(1)
@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_loading_test_fixture():
    management.call_command("loaddata", "fixtures/groups-and-permissions.json")
    management.call_command("loaddata", "fixtures/dev-environment-and-tests.json")


@pytest.mark.order(1)
@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_loading_demo_fixture():
    management.call_command("loaddata", "fixtures/groups-and-permissions.json")
    management.call_command("loaddata", "fixtures/demo-environment-data.json")


@pytest.mark.order(1)
@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_loading_groups_fixture():
    management.call_command("loaddata", "fixtures/groups-and-permissions.json")


@pytest.mark.parametrize(
    "view_kwargs, result, status_code, num_queries",
    (
        (
            {"model_label": "accounting.Charge"},
            {"detail": "Requesting choices for the provided model is not allowed."},
            400,
            0,
        ),
        (
            {"model_label": "accounting.Account"},
            {
                "id",
                "selected_steps",
                "account_title",
                "bank_name",
                "account_number",
                "branch_name",
                "branch_code",
                "iban",
            },
            200,
            1,
        ),
        (
            {"model_label": "authentication.Role"},
            {"name", "id", "selected_steps"},
            200,
            1,
        ),
        (
            {"model_label": "authentication.User"},
            {"username", "last_name", "first_name", "id", "slug", "selected_steps"},
            200,
            1,
        ),
        (
            {"model_label": "people.Vendor"},
            {"last_name", "first_name", "id", "slug", "selected_steps"},
            200,
            1,
        ),
        (
            {"model_label": "people.VendorType"},
            {"name", "id", "slug", "selected_steps"},
            200,
            1,
        ),
        (
            {"model_label": "people.Tenant"},
            {"last_name", "first_name", "id", "selected_steps"},
            200,
            1,
        ),
        (
            {"model_label": "people.Owner"},
            {"last_name", "first_name", "id", "selected_steps"},
            200,
            1,
        ),
        (
            {"model_label": "lease.RentalApplicationTemplate"},
            {"name", "id", "selected_steps"},
            200,
            1,
        ),
        (
            {"model_label": "lease.LeaseTemplate"},
            {"name", "id", "selected_steps"},
            200,
            1,
        ),
        (
            {"model_label": "lease.Applicant"},
            {"last_name", "first_name", "id", "selected_steps"},
            200,
            1,
        ),
        (
            {"model_label": "system_preferences.ContactCategory"},
            {"name", "id", "selected_steps"},
            200,
            1,
        ),
        (
            {"model_label": "system_preferences.InventoryItemType"},
            {"name", "id", "selected_steps"},
            200,
            1,
        ),
        (
            {"model_label": "system_preferences.InventoryLocation"},
            {"name", "id", "selected_steps"},
            200,
            1,
        ),
        (
            {"model_label": "system_preferences.PropertyType"},
            {"name", "id", "selected_steps"},
            200,
            1,
        ),
        (
            {"model_label": "system_preferences.Tag"},
            {"name", "id", "selected_steps"},
            200,
            1,
        ),
        (
            {"model_label": "system_preferences.Label"},
            {"name", "id", "selected_steps"},
            200,
            1,
        ),
        (
            {"model_label": "property.Property"},
            {"name", "id", "slug", "selected_steps", "is_late_fee_policy_configured", "is_occupied"},
            200,
            1,
        ),
        (
            {"model_label": "property.UnitType"},
            {"name", "id", "selected_steps"},
            200,
            1,
        ),
        (
            {"model_label": "property.Unit"},
            {
                "name",
                "id",
                "slug",
                "selected_steps",
                "is_occupied",
                "tenant_id",
                "tenant_first_name",
                "tenant_last_name",
            },
            200,
            1,
        ),
        (
            {"model_label": "maintenance.Inventory"},
            {"name", "id", "cost", "quantity", "selected_steps"},
            200,
            1,
        ),
        (
            {"model_label": "maintenance.ServiceRequest"},
            {"description", "id", "slug", "selected_steps"},
            200,
            1,
        ),
        (
            {"model_label": "maintenance.WorkOrder"},
            {"job_description", "id", "slug", "selected_steps"},
            200,
            1,
        ),
        (
            {"model_label": "maintenance.Project"},
            {"name", "id", "selected_steps"},
            200,
            1,
        ),
        (
            {"model_label": "communication.EmailTemplate"},
            {"subject", "body", "recipient_type", "individual_recipient_type", "id", "selected_steps"},
            200,
            1,
        ),
    ),
)
@pytest.mark.django_db
def test_model_choice_list_api_view(
    user_factory,
    api_rf,
    view_kwargs,
    result,
    status_code,
    num_queries,
    account_factory,
    email_template_factory,
    work_order_factory,
    project_factory,
    service_request_factory,
    inventory_factory,
    unit_factory,
    unit_type_factory,
    vendor_factory,
    property_factory,
    tag_factory,
    label_factory,
    property_type_factory,
    inventory_location_factory,
    inventory_item_type_factory,
    contact_category_factory,
    applicant_factory,
    rental_application_template_factory,
    owner_people_factory,
    lease_factory,
    vendor_type_factory,
    role_factory,
    lease_template_factory,
    subscription_factory,
):
    """
    Testing :py:meth:`core.views.ModelChoicesListAPIView.list` method.
    """
    subscription = subscription_factory()
    user = user_factory(associated_subscription=subscription)

    account_factory(subscription=subscription)
    email_template_factory(subscription=subscription)
    work_order_factory(subscription=subscription)
    project_factory(subscription=subscription)
    service_request_factory(subscription=subscription)
    inventory_factory(subscription=subscription)
    unit_factory(subscription=subscription)
    unit_type_factory(subscription=subscription)
    vendor_factory(subscription=subscription)
    property_factory(subscription=subscription)
    tag_factory(subscription=subscription)
    label_factory(subscription=subscription)
    property_type_factory(subscription=subscription)
    inventory_location_factory(subscription=subscription)
    inventory_item_type_factory(subscription=subscription)
    contact_category_factory(subscription=subscription)
    applicant_factory(subscription=subscription)
    rental_application_template_factory(subscription=subscription)
    owner_people_factory(subscription=subscription)
    lease_factory(subscription=subscription, status="ACTIVE")
    vendor_type_factory(subscription=subscription)
    role_factory(subscription=subscription)
    lease_template_factory(subscription=subscription)

    with assertNumQueries(num_queries):
        url = reverse("core:model_choices", kwargs=view_kwargs)
        request = api_rf.get(url, {}, format="json")
        request.user = user
        view = ModelChoicesListAPIView.as_view()
        response = view(request, **view_kwargs)

    assert response.status_code == status_code
    if status_code == 200:
        assert response.data[0].keys() == result
    else:
        assert response.data == result
