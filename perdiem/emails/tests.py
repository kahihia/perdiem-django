"""
:Created: 17 April 2016
:Author: Lucas Connors

"""

import mock

from emails.models import EmailSubscription
from emails.utils import create_unsubscribe_link
from perdiem.tests import PerDiemTestCase


class SubscribeTestCase(PerDiemTestCase):

    @mock.patch('emails.mailchimp.requests.put')
    def testSubscribeToNewsletterSuccess(self, mock_mailchimp_request):
        mock_mailchimp_request.return_value = mock.Mock(status_code=200)

        self.assertResponseRenders(
            '/accounts/settings/',
            method='POST',
            data={
                'action': 'email_preferences',
                'email': self.user.email,
                'subscription_all': True,
                'subscription_news': True,
                'subscription_artist_update': False,
            }
        )


class UnsubscribeWebTestCase(PerDiemTestCase):

    def setUp(self):
        super(UnsubscribeWebTestCase, self).setUp()
        EmailSubscription.objects.create(
            user=self.user,
            subscription=EmailSubscription.SUBSCRIPTION_ARTUP
        )

    def testUnsubscribe(self):
        unsubscribe_url = create_unsubscribe_link(self.user)
        self.assertResponseRenders(unsubscribe_url)

    def testUnsubscribeUnauthenticated(self):
        self.client.logout()
        unsubscribe_url = create_unsubscribe_link(self.user)
        self.assertResponseRenders(unsubscribe_url)

    def testUnsubscribeInvalidLink(self):
        self.client.logout()
        unsubscribe_url = '/unsubscribe/{user_id}/ALL/{invalid_token}/'.format(
            user_id=self.user.id,
            invalid_token='abc123'
        )
        response = self.assertResponseRenders(unsubscribe_url)
        self.assertIn("This link is invalid", response.content)
