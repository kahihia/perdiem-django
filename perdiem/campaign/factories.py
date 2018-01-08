from django.apps import apps as django_apps

import factory

from artist.factories import artistfactory_factory


def projectfactory_factory(apps):
    class ProjectFactory(factory.DjangoModelFactory):

        class Meta:
            model = apps.get_model('campaign', 'Project')

        artist = factory.SubFactory(artistfactory_factory(apps=apps))

    return ProjectFactory


def campaignfactory_factory(apps, point_to_project=True):
    class CampaignFactory(factory.DjangoModelFactory):

        class Meta:
            model = apps.get_model('campaign', 'Campaign')

        amount = 10000
        fans_percentage = 20

        # Allow the CampaignFactory to point to the artist
        # for migration test cases before the Project model was created
        if point_to_project:
            project = factory.SubFactory(projectfactory_factory(apps=apps))
        else:
            artist = factory.SubFactory(artistfactory_factory(apps=apps))

    return CampaignFactory


ProjectFactory = projectfactory_factory(apps=django_apps)
CampaignFactory = campaignfactory_factory(apps=django_apps)
