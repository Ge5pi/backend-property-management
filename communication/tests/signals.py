import pytest

from .models import Email


@pytest.mark.django_db
def test_populate_recipient_emails(email_factory, vendor_factory):
    """
    Testing :py:func:`communication.models.populate_recipient_emails` signal
    """
    vendor = vendor_factory()
    email = email_factory(vendors=(vendor,))
    email = email_factory(recipient_emails=[])

    assert email.recipient_emails == Email.objects.get_recipient_emails(email)
