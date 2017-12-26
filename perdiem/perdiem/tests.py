"""
:Created: 5 March 2016
:Author: Lucas Connors

"""

from accounts.factories import UserFactory
from pigeon.test import RenderTestCase


class PerDiemTestCase(RenderTestCase):

    USER_USERNAME = 'jsmith'
    USER_EMAIL = 'jsmith@example.com'

    @classmethod
    def setUpTestData(cls):
        super(PerDiemTestCase, cls).setUpTestData()
        cls.user = UserFactory(username=cls.USER_USERNAME, email=cls.USER_EMAIL, is_staff=True, is_superuser=True)

    def setUp(self):
        self.client.login(username=self.USER_USERNAME, password=UserFactory._PASSWORD)


class HealthCheckWebTestCase(RenderTestCase):

    def get200s(self):
        return [
            '/health-check/',
        ]


class ExtrasWebTestCase(RenderTestCase):

    def get200s(self):
        return [
            '/faq/',
            '/trust/',
            '/terms/',
            '/privacy/',
            '/contact/',
            '/resources/',
        ]

    def testContact(self):
        self.assertResponseRedirects(
            '/contact/',
            '/contact/thanks',
            method='POST',
            data={'inquiry': 'General Inquiry', 'email': 'msmith@example.com', 'message': 'Hello World!'}
        )
