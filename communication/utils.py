import os

import boto3  # type: ignore[import]
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import Email


def send_email_from_email_model(email: Email):
    message = render_to_string("communication/emails/email_template.html", {"email": email})
    plain_message = strip_tags(message)
    email_message = EmailMessage(
        email.subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        email.recipient_emails,
    )
    for attachment in email.attachments.all():
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        s3_client.download_file(settings.AWS_STORAGE_BUCKET_NAME, attachment.file, attachment.name)
        email_message.attach_file(attachment.name)

        os.remove(attachment.name)
    email_message.send(fail_silently=False)
