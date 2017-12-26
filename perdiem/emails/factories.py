import factory

from accounts.factories import UserFactory
from emails.models import EmailSubscription


class EmailSubscriptionFactory(factory.DjangoModelFactory):

    class Meta:
        model = EmailSubscription

    user = factory.SubFactory(UserFactory)
