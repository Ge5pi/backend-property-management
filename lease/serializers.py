from typing import Any, Optional

from django.db.models import Value
from django.db.models.functions import Concat
from rest_framework import serializers

from authentication.serializers import UserSerializer
from core.serializers import ModifiedByAbstractSerializer
from lease.models import (
    Applicant,
    Lease,
    LeaseTemplate,
    RentalApplication,
    RentalApplicationAdditionalIncome,
    RentalApplicationAttachment,
    RentalApplicationDependent,
    RentalApplicationEmergencyContact,
    RentalApplicationFinancialInformation,
    RentalApplicationPets,
    RentalApplicationResidentialHistory,
    RentalApplicationTemplate,
    SecondaryTenant,
)
from people.models import Owner


class RentalApplicationTemplateSerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = RentalApplicationTemplate
        fields = (
            "id",
            "name",
            "description",
            "general_info",
            "personal_details",
            "rental_history",
            "financial_info",
            "dependents_info",
            "other_info",
            "created_at",
        )


class RentalApplicationAttachmentSerializer(ModifiedByAbstractSerializer):
    created_by = UserSerializer(many=False, read_only=True)

    class Meta:
        model = RentalApplicationAttachment
        fields = (
            "id",
            "name",
            "created_by",
            "file",
            "rental_application",
            "file_type",
            "updated_at",
        )
        read_only_fields = ("id", "created_by")


class ApplicantSerializer(ModifiedByAbstractSerializer):
    property_id = serializers.IntegerField(source="unit.parent_property.id", read_only=True)
    property_name = serializers.CharField(source="unit.parent_property.name", read_only=True)
    property_rental_application_template = serializers.IntegerField(
        source="unit.parent_property.rental_application_template.id", read_only=True
    )
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    status_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Applicant
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "allow_email_for_rental_application",
            "unit",
            "rental_application",
            "status_percentage",
            "property_id",
            "property_name",
            "unit_name",
            "property_rental_application_template",
        )
        read_only_fields = ("id", "rental_application", "status_percentage")

    def get_status_percentage(self, obj) -> float:
        try:
            template = obj.unit.parent_property.rental_application_template
            application = obj.rental_application
            template_forms = 0
            application_form = 0
            if template and application:
                if template.general_info:
                    template_forms += 1
                if template.personal_details:
                    template_forms += 1
                if template.rental_history:
                    template_forms += 1
                if template.financial_info:
                    template_forms += 1
                if template.dependents_info:
                    template_forms += 1
                if template.other_info:
                    template_forms += 1

                if application.is_general_info_filled:
                    application_form += 1
                if application.is_personal_details_filled:
                    application_form += 1
                if application.is_rental_history_filled:
                    application_form += 1
                if application.is_financial_info_filled:
                    application_form += 1
                if application.is_dependents_filled:
                    application_form += 1
                if application.is_other_info_filled:
                    application_form += 1

            percentage = application_form / template_forms * 100

        except Exception:
            percentage = 0
        return percentage


class RentalApplicationEmergencyContactSerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = RentalApplicationEmergencyContact
        fields = ("id", "name", "phone_number", "relationship", "address", "rental_application")


class RentalApplicationResidentialHistorySerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = RentalApplicationResidentialHistory
        fields = (
            "id",
            "current_address",
            "current_address_2",
            "current_city",
            "current_zip_code",
            "current_country",
            "resident_from",
            "resident_to",
            "landlord_name",
            "landlord_phone_number",
            "landlord_email",
            "reason_of_leaving",
            "rental_application",
            "monthly_rent",
            "current_state",
        )


class RentalApplicationFinancialInformationSerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = RentalApplicationFinancialInformation
        fields = (
            "id",
            "name",
            "account_type",
            "bank",
            "account_number",
            "rental_application",
        )


class RentalApplicationAdditionalIncomeSerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = RentalApplicationAdditionalIncome
        fields = (
            "id",
            "monthly_income",
            "source_of_income",
            "rental_application",
        )


class RentalApplicationDependentSerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = RentalApplicationDependent
        fields = (
            "id",
            "first_name",
            "last_name",
            "birthday",
            "relationship",
            "rental_application",
        )


class RentalApplicationPetsSerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = RentalApplicationPets
        fields = (
            "id",
            "name",
            "pet_type",
            "weight",
            "age",
            "rental_application",
        )


class RentalApplicationSerializer(ModifiedByAbstractSerializer):
    slug = serializers.CharField(read_only=True)
    lease_id = serializers.SerializerMethodField()

    class Meta:
        model = RentalApplication
        fields = (
            "id",
            "slug",
            "applicant",
            "status",
            "get_status_display",
            "desired_move_in_date",
            "legal_first_name",
            "middle_name",
            "legal_last_name",
            "application_type",
            "get_application_type_display",
            "phone_number",
            "emails",
            "notes",
            "birthday",
            "ssn_or_tin",
            "driving_license_number",
            "employer_name",
            "employer_address",
            "employer_phone_number",
            "employment_city",
            "employment_zip_code",
            "employment_country",
            "monthly_salary",
            "position_held",
            "years_worked",
            "supervisor_name",
            "supervisor_phone_number",
            "supervisor_email",
            "supervisor_title",
            "is_defendant_in_any_lawsuit",
            "is_convicted",
            "have_filed_case_against_landlord",
            "is_smoker",
            "general_info",
            "personal_details",
            "rental_history",
            "financial_info",
            "dependents_info",
            "other_info",
            "is_general_info_filled",
            "is_personal_details_filled",
            "is_rental_history_filled",
            "is_financial_info_filled",
            "is_dependents_filled",
            "is_other_info_filled",
            "lease_id",
        )
        read_only_fields = (
            "general_info",
            "personal_details",
            "rental_history",
            "financial_info",
            "dependents_info",
            "other_info",
            "lease_id",
            "applicant",
        )

    def get_lease_id(self, obj) -> Optional[int]:
        if isinstance(obj, RentalApplication):
            leases = obj.leases.all()
            if leases.exists():
                return leases.latest("created_at").id
            else:
                return None
        else:
            return None


class LeaseTemplateSerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = LeaseTemplate
        fields = (
            "id",
            "name",
            "description",
            "rules_and_policies",
            "condition_of_premises",
            "right_of_inspection",
            "conditions_of_moving_out",
            "releasing_policies",
            "final_statement",
            "created_at",
        )


class SecondaryTenantSerializer(ModifiedByAbstractSerializer):
    class Meta:
        model = SecondaryTenant
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "birthday",
            "phone_number",
            "tax_payer_id",
            "description",
            "lease",
        )


class LeaseSerializer(ModifiedByAbstractSerializer):
    property_id = serializers.IntegerField(source="unit.parent_property.id", read_only=True)
    property_name = serializers.CharField(source="unit.parent_property.name", read_only=True)
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    tenant_first_name = serializers.CharField(source="primary_tenant.first_name", read_only=True)
    tenant_last_name = serializers.CharField(source="primary_tenant.last_name", read_only=True)
    applicant_id = serializers.IntegerField(source="rental_application.applicant.id", read_only=True)
    applicant = serializers.PrimaryKeyRelatedField(queryset=Applicant.objects.all(), required=True, write_only=True)
    owners = serializers.SerializerMethodField()

    class Meta:
        model = Lease
        fields = (
            "id",
            "rental_application",
            "lease_type",
            "get_lease_type_display",
            "start_date",
            "end_date",
            "lease_template",
            "rent_cycle",
            "get_rent_cycle_display",
            "amount",
            "gl_account",
            "description",
            "due_date",
            "status",
            "get_status_display",
            "closed_on",
            "unit",
            "created_at",
            "primary_tenant",
            "property_id",
            "property_name",
            "unit_name",
            "tenant_first_name",
            "tenant_last_name",
            "owners",
            "applicant_id",
            "applicant",
        )
        read_only_fields = ("id", "primary_tenant", "lease_template", "rental_application", "unit")

    def create(self, validated_data: Any) -> Any:
        applicant = validated_data.pop("applicant")
        validated_data["rental_application"] = applicant.rental_application
        validated_data["unit"] = applicant.unit
        return super().create(validated_data)

    def get_owners(self, obj):
        if isinstance(obj, Lease):
            owner_people_ids = obj.unit.parent_property.owners.values_list("owner")
            owner_people = Owner.objects.filter(id__in=owner_people_ids).annotate(
                full_name=Concat("first_name", Value(" "), "last_name")
            )
            return list(owner_people.values_list("full_name", flat=True))
        else:
            return []
