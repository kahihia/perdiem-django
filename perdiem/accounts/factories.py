from django.contrib.auth.models import User

import factory

from accounts.models import UserAvatar


class UserFactory(factory.DjangoModelFactory):

    _PASSWORD = 'abc123'

    class Meta:
        model = User

    username = factory.Sequence(lambda n: "user_{n}".format(n=n))
    password = factory.PostGenerationMethodCall('set_password', _PASSWORD)
    email = factory.LazyAttribute(lambda user: "{username}@gmail.com".format(username=user.username))


class UserAvatarFactory(factory.DjangoModelFactory):

    class Meta:
        model = UserAvatar

    user = factory.SubFactory(UserFactory)
