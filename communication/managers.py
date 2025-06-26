from django.db import models
from django.db.models import BooleanField, Case, ExpressionWrapper, Q, QuerySet, Value, When
from django.db.models.functions import Now

from lease.models import Lease


class EmailAbstractManager(models.Manager):
    def get_recipient_emails(self, email):
        if email.recipient_type == "INDIVIDUAL":
            if email.individual_recipient_type == "TENANT":
                return list(email.tenants.values_list("email", flat=True))
            elif email.individual_recipient_type == "OWNER":
                emails = [
                    *email.owners.values_list("personal_emails", flat=True),
                    *email.owners.values_list("company_emails", flat=True),
                ]
                emails = [email for sublist in emails for email in sublist]
                return list(emails)
            elif email.individual_recipient_type == "VENDOR":
                emails = [
                    *email.vendors.values_list("personal_emails", flat=True),
                    *email.vendors.values_list("business_emails", flat=True),
                ]
                emails = [email for sublist in emails for email in sublist]
                return list(emails)
        elif email.recipient_type == "PROPERTY":
            leases_ids = email.units.values_list("leases__id", flat=True)
            leases = Lease.objects.filter(id__in=leases_ids, status=Lease.LeaseStatus.ACTIVE)
            tenants = leases.values_list("primary_tenant__email", flat=True)
            return list(tenants)


class AnnouncementQuerySet(QuerySet):
    def annotate_status(self):
        return self.annotate(
            expired=ExpressionWrapper(Q(expiry_date__lt=Now()), output_field=BooleanField()),
            status=Case(
                When(expired=True, then=Value("Expired")),
                When(expired=False, then=Value("Active")),
                default=Value("Expired"),
            ),
        )


AnnouncementManager = EmailAbstractManager.from_queryset(AnnouncementQuerySet)
