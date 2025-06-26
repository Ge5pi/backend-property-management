import django_filters  # type: ignore[import-untyped]
from django_filters import rest_framework as rest_framework_filters
from rest_framework import filters


class ModelChoicesSearchFilter(filters.SearchFilter):
    """
    A customized search filter used by :py:class:`app.core.views.ModelChoicesListAPIView` that allows the searching for
    different models dynamically.
    """

    def get_search_fields(self, view, request):
        return view.get_search_fields()


class ModelChoicesFilterSet(django_filters.rest_framework.DjangoFilterBackend):
    """
    A customized filter used by :py:class:`app.core.views.ModelChoicesListAPIView` that allows the filtering for
    different models dynamically.
    """

    def get_filterset_class(self, view, queryset=None):
        setattr(view, "filterset_fields", view.filterset_config.get(view.source_model))
        return super().get_filterset_class(view, queryset)


class UpcomingActivityFilter(rest_framework_filters.FilterSet):
    title = rest_framework_filters.CharFilter(lookup_expr="icontains")
    date_month = rest_framework_filters.NumberFilter(field_name="date", lookup_expr="month")
    date_year = rest_framework_filters.NumberFilter(field_name="date", lookup_expr="year")
    label_id = rest_framework_filters.CharFilter(method="filter_label_id")

    def filter_label_id(self, queryset, name, value):
        value = value.split(",")
        return queryset.filter(label_id__in=value)
