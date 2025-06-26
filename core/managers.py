from django.db.models import Value
from django.db.models.fields import CharField
from django.db.models.functions import Cast, Concat


class SlugQuerysetMixin:
    """
    Queryset Mixin for adding slug field to Model queryset.
    It reads `SLUG` value from model and add `id` with it to make slug.
    """

    def annotate_slug(self):
        if not hasattr(self.model, "SLUG"):
            raise KeyError(f"SLUG value must be provided in {self.model._meta.verbose_name}")
        return self.annotate(slug=Concat(Value(f"{self.model.SLUG}-"), Cast("id", output_field=CharField())))
