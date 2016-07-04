"""
:Created: 12 March 2016
:Author: Lucas Connors

"""

from perdiem.tests import PerDiemTestCase


class CampaignAdminWebTestCase(PerDiemTestCase):

    def get200s(self):
        return [
            '/admin/campaign/',
            '/admin/campaign/project/',
            '/admin/campaign/project/add/',
            '/admin/campaign/project/{project_id}/change/'.format(project_id=self.project.id),
            '/admin/campaign/campaign/',
            '/admin/campaign/campaign/add/',
            '/admin/campaign/campaign/{campaign_id}/change/'.format(campaign_id=self.campaign.id),
            '/admin/campaign/investment/',
            '/admin/campaign/revenuereport/',
            '/admin/campaign/revenuereport/add/',
            '/admin/campaign/revenuereport/{revenue_report_id}/change/'.format(revenue_report_id=self.revenue_report.id),
        ]

    def testCampaignRaisingZeroIsAlreadyFunded(self):
        self.campaign.amount = 0
        self.campaign.save()
        self.assertEquals(self.campaign.percentage_funded(), 100)


class CampaignWebTestCase(PerDiemTestCase):

    def get200s(self):
        return [
            '/leaderboard/',
        ]
