from rest_framework import serializers

from accounting.models import Invoice


class PaymentIntentForInvoiceSerializer(serializers.Serializer):
    invoice = serializers.PrimaryKeyRelatedField(queryset=Invoice.objects.all())
