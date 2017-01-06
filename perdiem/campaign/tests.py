"""
:Created: 12 March 2016
:Author: Lucas Connors

"""

import datetime

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
            '/admin/campaign/revenuereport/{revenue_report_id}/change/'.format(
                revenue_report_id=self.revenue_report.id
            ),
        ]

    def testCampaignRaisingZeroIsAlreadyFunded(self):
        self.campaign.amount = 0
        self.campaign.save()
        self.assertEquals(self.campaign.percentage_funded(), 100)

    def testCampaignEndCannotComeBeforeStart(self):
        start_datetime = datetime.datetime(year=2017, month=2, day=1)
        end_datetime = datetime.datetime(year=2017, month=1, day=1)

        data = {
            'project': self.project.id,
            'amount': self.CAMPAIGN_AMOUNT,
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
        response = self.assertResponseRenders(
            '/admin/campaign/campaign/add/',
            method='POST',
            data=data,
            has_form_error=True
        )
        self.assertIn("Campaign cannot end before it begins.", response.content)


class CampaignWebTestCase(PerDiemTestCase):

    def get200s(self):
        return [
            '/stats/',
        ]
