from django.apps import apps as django_apps

import factory

from accounts.factories import UserFactory
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


class CustomerFactory(factory.DjangoModelFactory):

    class Meta:
        model = django_apps.get_model('pinax_stripe', 'Customer')

    user = factory.SubFactory(UserFactory)


class ChargeFactory(factory.DjangoModelFactory):

    class Meta:
        model = django_apps.get_model('pinax_stripe', 'Charge')

    customer = factory.SubFactory(CustomerFactory)
    paid = True
    refunded = False


class InvestmentFactory(factory.DjangoModelFactory):

    class Meta:
        model = django_apps.get_model('campaign', 'Investment')

    charge = factory.SubFactory(ChargeFactory)
    campaign = factory.SubFactory(CampaignFactory)
