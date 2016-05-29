"""
:Created: 29 May 2016
:Author: Lucas Connors

"""

from perdiem.tests import PerDiemTestCase

from artist.models import Update


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


class DeleteUpdateTestCase(PerDiemTestCase):

    def setUp(self):
        super(DeleteUpdateTestCase, self).setUp()
        self.url = '/api/update/{update_id}/'
        self.valid_url = self.url.format(update_id=self.update.id)

    def testDeleteUpdate(self):
        response = self.assertResponseRenders(self.valid_url, status_code=204, method='DELETE')

    def testDeleteUpdateRequiresValidUpdateId(self):
        response = self.assertResponseRenders(self.url.format(update_id=0), status_code=403)

    def testDeleteUpdateFailsWithoutPermission(self):
        # Logout from being a superuser
        self.client.logout()

        # Delete Update API requires permission
        # but you're not authenticated
        self.assertResponseRenders(self.valid_url, status_code=403, method='DELETE')

        # Login as ordinary user
        self.client.login(
            username=self.ORDINARY_USER_USERNAME,
            password=self.USER_PASSWORD
        )

        # Delete Update API the user to be an ArtistAdmin (or superuser)
        # but you don't have access
        self.assertResponseRenders(self.valid_url, status_code=403)

    def testDeleteUpdateOnlyAllowsArtistAdminsToUpdateTheirArtists(self):
        # Logout from being a superuser
        self.client.logout()

        # Login as manager
        self.client.login(
            username=self.MANAGER_USER_USERNAME,
            password=self.USER_PASSWORD
        )

        # Delete Update API allows ArtistAdmins to update
        self.assertResponseRenders(self.valid_url, status_code=204, method='DELETE')

        # Delete Update API does not allow ArtistAdmins
        # to update artists they don't belong to
        update = Update.objects.create(artist=self.artist_no_campaign, text=self.ARTIST_UPDATE)
        self.assertResponseRenders(self.url.format(update_id=update.id), status_code=403, method='DELETE')
