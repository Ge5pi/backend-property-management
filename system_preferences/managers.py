from django.db import models
from django.db.models import Count
from django.db.models.query import QuerySet


class PropertyTypeQuerySet(QuerySet):
    def annotate_num_records(self):
        return self.annotate(items_count=Count("properties"))


PropertyTypeManager = models.Manager.from_queryset(PropertyTypeQuerySet)


class TagQuerySet(QuerySet):
    def annotate_num_records(self):
        return self.annotate(
            items_count=Count("unit_types", distinct=True)
            + Count("notes", distinct=True)
            + Count("unit", distinct=True)
        )


TagManager = models.Manager.from_queryset(TagQuerySet)


class LabelQuerySet(QuerySet):
    def annotate_num_records(self):
        return self.annotate(
            items_count=Count("unitupcomingactivity")
            + Count("tenantupcomingactivity")
            + Count("ownerupcomingactivity")
            + Count("propertyupcomingactivity")
        )


LabelManager = models.Manager.from_queryset(LabelQuerySet)


class InventoryItemTypeQuerySet(QuerySet):
    def annotate_num_records(self):
        return self.annotate(items_count=Count("inventory"))


InventoryItemTypeManager = models.Manager.from_queryset(InventoryItemTypeQuerySet)


class InventoryLocationQuerySet(QuerySet):
    def annotate_num_records(self):
        return self.annotate(items_count=Count("inventory"))


InventoryLocationManager = models.Manager.from_queryset(InventoryLocationQuerySet)


class ContactCategoryQuerySet(QuerySet):
    def annotate_num_records(self):
        return self.annotate(items_count=Count("contacts"))


ContactCategoryManager = models.Manager.from_queryset(ContactCategoryQuerySet)
