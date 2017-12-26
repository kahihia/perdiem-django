import factory

from artist.factories import ArtistFactory
from campaign.models import Campaign, Project


class ProjectFactory(factory.DjangoModelFactory):

    class Meta:
        model = Project

    artist = factory.SubFactory(ArtistFactory)


class CampaignFactory(factory.DjangoModelFactory):

    class Meta:
        model = Campaign

    project = factory.SubFactory(ProjectFactory)
    amount = 10000
    fans_percentage = 20
