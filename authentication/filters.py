from typing import List

from django_filters import rest_framework as filters

from .models import User


class UserFilter(filters.FilterSet):
    """
    Filter class for :model:`authentication.User` model.
    """

    is_tenant = filters.BooleanFilter()

    class Meta:
        model = User
        fields: List[str] = []  # ignore:[var-annotated]
