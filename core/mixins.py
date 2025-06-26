class FilterQuerysetByAssociatedSubscriptionMixin:
    """
    Mixin to filter queryset by associated subscription of current user.
    NOTE: This mixin on only work on `queryset` attribute. If `get_queryset()` is overridden on view level,
    call `super().get_queryset()` to get filtered data by subscription
    """

    def get_queryset(self):
        if self.queryset is None:
            raise AttributeError(f"'{self.__class__.__name__}' should include a `queryset` attribute.")

        queryset = super().get_queryset()
        return queryset.filter(subscription=self.request.user.associated_subscription)
