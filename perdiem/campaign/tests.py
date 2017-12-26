"""
:Created: 12 March 2016
:Author: Lucas Connors

"""

import datetime

from pigeon.test import RenderTestCase

from campaign.factories import CampaignFactory, ProjectFactory
from perdiem.tests import PerDiemTestCase


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

    def testCampaignRaisingZeroIsAlreadyFunded(self):
        campaign = CampaignFactory(amount=0)
        self.assertEquals(campaign.percentage_funded(), 100)

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
