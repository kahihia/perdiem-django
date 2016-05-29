"""
:Created: 29 May 2016
:Author: Lucas Connors

"""

from perdiem.tests import PerDiemTestCase


class CoordinatesFromAddressTestCase(PerDiemTestCase):

    url = '/api/coordinates/?address={address}'
    valid_url = url.format(address='Willowdale%2C+Toronto%2C+Ontario%2C+Canada')

    def testCoordinatesFromAddress(self):
        response = self.assertJsonResponseRenders(self.valid_url)
        lat, lon = response['latitude'], response['longitude']
        self.assertAlmostEquals(lat, 43.7689, places=2)
        self.assertAlmostEquals(lon, -79.4138, places=2)

    def testCoordinatesFromAddressRequiresAddress(self):
        for url in ['/api/coordinates/', self.url.format(address=''),]:
            self.assertResponseRenders(url, status_code=400)

    def testCoordinatesFromAddressFailsWithoutPermission(self):
        # Logout from being a superuser
        self.client.logout()

        # Coordinates from Address API requires permission
        # but you're not authenticated
        self.assertResponseRenders(self.valid_url, status_code=403)

        # Login as an ordinary user
        self.client.login(
            username=self.ORDINARY_USER_USERNAME,
            password=self.USER_PASSWORD
        )

        # Coordinates from Address API requires permission
        # but you don't have the required permission
        self.assertResponseRenders(self.valid_url, status_code=403)
