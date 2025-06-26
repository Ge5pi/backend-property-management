import factory  # type: ignore[import]


class SubscriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "subscription.Subscription"
