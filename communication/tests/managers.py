from datetime import timedelta

import pytest
from django.utils import timezone

from .models import Announcement, Email


@pytest.mark.django_db
def test_email_abstract_manager(email_factory, vendor_factory):
    """
    Testing :py:class:`communication.managers.EmailAbstractManager` abstract manager
    """
    vendor = vendor_factory()
    email = email_factory(vendors=(vendor,))
    recipient_emails = Email.objects.get_recipient_emails(email)
    assert isinstance(recipient_emails, list)
    assert len(Email.objects.get_recipient_emails(email)) > 0


@pytest.mark.django_db
def test_announcement_manager(announcement_factory):
    """
    Testing :py:class:`communication.managers.AnnouncementQuerySet.annotate_status` abstract manager
    """
    expiry_1 = timezone.now() + timedelta(days=1)
    expiry_2 = timezone.now() - timedelta(days=1)
    announcement_factory(expiry_date=expiry_1.date())
    announcement_factory(expiry_date=expiry_2.date())
    announcements = Announcement.objects.annotate_status()
    assert announcements[0].status == "Active"
    assert announcements[1].status == "Expired"
