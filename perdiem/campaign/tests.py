"""
:Created: 12 March 2016
:Author: Lucas Connors

"""

import datetime

from django.test import TestCase

import factory
from pigeon.test import RenderTestCase

from artist.factories import ArtistFactory
from campaign.factories import CampaignFactory, InvestmentFactory, ProjectFactory, campaignfactory_factory
from perdiem.tests import MigrationTestCase, PerDiemTestCase


class CreateInitialProjectsMigrationTestCase(MigrationTestCase):

    migrate_from = '0005_auto_20160618_2310'
    migrate_to = '0006_auto_20160618_2351'

    def setUpBeforeMigration(self, apps):
        # Create a campaign
        CampaignFactoryForMigrationTestCase = campaignfactory_factory(apps=apps, point_to_project=False)
        self.campaign = CampaignFactoryForMigrationTestCase()

    def testProjectsCreatedFromCampaigns(self):
        Project = self.apps.get_model('campaign', 'Project')

        # Verify that a project was created from the campaign
        self.assertEquals(Project.objects.count(), 1)

        # Verify that the project reason comes from the campaign reason
        project = Project.objects.get()
        self.assertEquals(project.reason, self.campaign.reason)


class PointArtistPercentageBreakdownsAndRevenueReportsToProjectsMigrationTestCase(MigrationTestCase):

    migrate_from = '0007_auto_20160618_2352'
    migrate_to = '0008_auto_20160618_2352'

    def setUpBeforeMigration(self, apps):
        CampaignFactoryForMigrationTestCase = campaignfactory_factory(apps=apps)

        class ArtistPercentageBreakdownFactoryForMigrationTestCase(factory.DjangoModelFactory):
            class Meta:
                model = apps.get_model('campaign', 'ArtistPercentageBreakdown')
            campaign = factory.SubFactory(CampaignFactoryForMigrationTestCase)

        class RevenueReportFactoryForMigrationTestCase(factory.DjangoModelFactory):
            class Meta:
                model = apps.get_model('campaign', 'RevenueReport')
            campaign = factory.SubFactory(CampaignFactoryForMigrationTestCase)

        # Create an ArtistPercentageBreakdown and RevenueReport
        self.artistpercentagebreakdown = ArtistPercentageBreakdownFactoryForMigrationTestCase(percentage=50)
        campaign = self.artistpercentagebreakdown.campaign
        self.revenue_report = RevenueReportFactoryForMigrationTestCase(campaign=campaign, amount=1000)

    def testArtistPercentageBreakdownAndRevenueReportPointsToProject(self):
        Campaign = self.apps.get_model('campaign', 'Campaign')
        campaign = Campaign.objects.get()
        self.artistpercentagebreakdown.refresh_from_db()
        self.assertEquals(self.artistpercentagebreakdown.project.id, campaign.project.id)
        self.revenue_report.refresh_from_db()
        self.assertEquals(self.revenue_report.project.id, campaign.project.id)


class UserProfileContextTestCase(TestCase):

    def testUserProfileContextContainsInvestments(self):
        investment = InvestmentFactory()
        self.assertGreater(investment.charge.customer.user.userprofile.profile_context()['total_investments'], 0)


class CampaignModelTestCase(TestCase):

    def testCampaignRaisingZeroIsAlreadyFunded(self):
        campaign = CampaignFactory(amount=0)
        self.assertEquals(campaign.percentage_funded(), 100)


class CampaignAdminWebTestCase(PerDiemTestCase):

    def setUp(self):
        super(CampaignAdminWebTestCase, self).setUp()
        project = ProjectFactory()
        start_datetime = datetime.datetime(year=2017, month=2, day=1)
        end_datetime = datetime.datetime(year=2017, month=3, day=1)
        self.campaign_add_data = {
            'project': project.id,
            'amount': 10000,
            'value_per_share': 1,
            'start_datetime_0': start_datetime.strftime('%Y-%m-%d'),
            'start_datetime_1': start_datetime.strftime('%H:%M:%S'),
            'end_datetime_0': end_datetime.strftime('%Y-%m-%d'),
            'end_datetime_1': end_datetime.strftime('%H:%M:%S'),
            'use_of_funds': '',
            'fans_percentage': 50,
            'expense_set-TOTAL_FORMS': 0,
            'expense_set-INITIAL_FORMS': 0,
        }

    def testAddCampaign(self):
        self.assertResponseRedirects(
            '/admin/campaign/campaign/add/',
            '/admin/campaign/campaign/',
            method='POST',
            data=self.campaign_add_data
        )

    def testCampaignEndCannotComeBeforeStart(self):
        # Set the end datetime to a value from the past
        data = self.campaign_add_data.copy()
        end_datetime = datetime.datetime(year=2017, month=1, day=1)
        data.update({
            'end_datetime_0': end_datetime.strftime('%Y-%m-%d'),
            'end_datetime_1': end_datetime.strftime('%H:%M:%S'),
        })

        # Campaigns cannot be added that have an end datetime before the start
        response = self.assertResponseRenders(
            '/admin/campaign/campaign/add/',
            method='POST',
            data=data,
            has_form_error=True
        )
        self.assertIn("Campaign cannot end before it begins.", response.content)

    def testCannotAddCampaignWithoutTime(self):
        for dt in ['start', 'end']:
            # Erase the time from campaign add POST data
            data = self.campaign_add_data.copy()
            del data['{dt}_datetime_1'.format(dt=dt)]

            # Fail to create a campaign without the time component
            self.assertResponseRenders(
                '/admin/campaign/campaign/add/',
                method='POST',
                data=data,
                has_form_error=True
            )


class CampaignWebTestCase(RenderTestCase):

    def get200s(self):
        return [
            '/stats/',
        ]
