from django.utils.text import slugify

import factory

from campaign.factories import ProjectFactory
from music.models import Album


class AlbumFactory(factory.DjangoModelFactory):

    class Meta:
        model = Album

    project = factory.SubFactory(ProjectFactory)
    name = factory.Sequence(lambda n: 'Album #{n}'.format(n=n))
    slug = factory.LazyAttribute(lambda album: slugify(album.name))
