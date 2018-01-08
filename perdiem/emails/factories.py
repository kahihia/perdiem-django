from django.apps import apps

import factory

from accounts.factories import UserFactory


class EmailSubscriptionFactory(factory.DjangoModelFactory):

    class Meta:
        model = apps.get_model('emails', 'EmailSubscription')

    user = factory.SubFactory(UserFactory)
