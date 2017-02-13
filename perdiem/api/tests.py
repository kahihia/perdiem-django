"""
:Created: 29 May 2016
:Author: Lucas Connors

"""

import mock

from geopy.exc import GeocoderTimedOut

from perdiem.tests import PerDiemTestCase
from artist.models import Update


class CoordinatesFromAddressTestCase(PerDiemTestCase):

    url = '/api/coordinates/?address={address}'
    valid_url = url.format(address='Willowdale%2C+Toronto%2C+Ontario%2C+Canada')

    @mock.patch('api.views.Nominatim.geocode')
    def testCoordinatesFromAddress(self, mock_geocode):
        # First the Geocoder service fails and so we return 503
        mock_geocode.side_effect = GeocoderTimedOut
        self.assertAPIResponseRenders(self.valid_url, status_code=503)

        # Then the Geocoder service kicks back online and we succeed
        mock_geocode.side_effect = None
        mock_geocode.return_value = mock.Mock(latitude=43.766751, longitude=-79.410332)
        response = self.assertAPIResponseRenders(self.valid_url)
        lat, lon = response['latitude'], response['longitude']
        self.assertEquals(lat, 43.7668)
        self.assertEquals(lon, -79.4103)

    def testCoordinatesFromAddressRequiresAddress(self):
        for url in ['/api/coordinates/', self.url.format(address='')]:
            self.assertAPIResponseRenders(url, status_code=400)

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
        self.assertAPIResponseRenders(self.valid_url, status_code=204, method='DELETE')

    def testDeleteUpdateRequiresValidUpdateId(self):
        self.assertResponseRenders(self.url.format(update_id=0), status_code=403)

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
