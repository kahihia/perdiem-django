from django.utils.text import slugify

import factory

from accounts.factories import UserFactory
from artist.models import Artist, ArtistAdmin, Update


class ArtistFactory(factory.DjangoModelFactory):

    class Meta:
        model = Artist

    name = factory.Sequence(lambda n: 'Artist {n}'.format(n=n))
    slug = factory.LazyAttribute(lambda artist: slugify(artist.name))

    # Willowdale, Toronto, Ontario, Canada
    lat = 43.7689
    lon = -79.4138


class ArtistAdminFactory(factory.DjangoModelFactory):

    class Meta:
        model = ArtistAdmin

    artist = factory.SubFactory(ArtistFactory)
    user = factory.SubFactory(UserFactory)


class UpdateFactory(factory.DjangoModelFactory):

    class Meta:
        model = Update

    artist = factory.SubFactory(ArtistFactory)
