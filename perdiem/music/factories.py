from django.apps import apps
from django.utils.text import slugify

import factory

from campaign.factories import ProjectFactory


class AlbumFactory(factory.DjangoModelFactory):

    class Meta:
        model = apps.get_model('music', 'Album')

    project = factory.SubFactory(ProjectFactory)
    name = factory.Sequence(lambda n: 'Album #{n}'.format(n=n))
    slug = factory.LazyAttribute(lambda album: slugify(album.name))
