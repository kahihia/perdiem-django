from django.apps import apps
from django.conf import settings

import factory


class UserFactory(factory.DjangoModelFactory):

    _PASSWORD = 'abc123'

    class Meta:
        model = apps.get_model(settings.AUTH_USER_MODEL)

    username = factory.Sequence(lambda n: "user_{n}".format(n=n))
    password = factory.PostGenerationMethodCall('set_password', _PASSWORD)
    email = factory.LazyAttribute(lambda user: "{username}@gmail.com".format(username=user.username))


class UserAvatarFactory(factory.DjangoModelFactory):

    class Meta:
        model = apps.get_model('accounts', 'UserAvatar')

    user = factory.SubFactory(UserFactory)
