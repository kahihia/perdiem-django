"""
:Created: 17 April 2016
:Author: Lucas Connors

"""

from emails.utils import create_unsubscribe_link
from perdiem.tests import PerDiemTestCase


class UnsubscribeWebTestCase(PerDiemTestCase):

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
