from django.apps import apps

import factory

from artist.factories import ArtistFactory


class ProjectFactory(factory.DjangoModelFactory):

    class Meta:
        model = apps.get_model('campaign', 'Project')

    artist = factory.SubFactory(ArtistFactory)


class CampaignFactory(factory.DjangoModelFactory):

    class Meta:
        model = apps.get_model('campaign', 'Campaign')

    project = factory.SubFactory(ProjectFactory)
    amount = 10000
    fans_percentage = 20
