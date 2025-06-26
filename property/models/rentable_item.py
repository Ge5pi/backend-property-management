from django.db import models

from core.models import CommonInfoAbstractModel


class RentableItem(CommonInfoAbstractModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    gl_account = models.CharField(max_length=255)
    tenant = models.ForeignKey("people.Tenant", related_name="rentable_items", on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    parent_property = models.ForeignKey("property.Property", related_name="rentable_items", on_delete=models.CASCADE)

    def __str__(self):
        return self.name
