"""
:Created: 12 March 2016
:Author: Lucas Connors

"""

import mock

from geopy.exc import GeocoderTimedOut

from perdiem.tests import PerDiemTestCase


class ArtistAdminWebTestCase(PerDiemTestCase):

    def get200s(self):
        return [
            '/admin/artist/',
            '/admin/artist/genre/',
            '/admin/artist/genre/add/',
            '/admin/artist/genre/{genre_id}/change/'.format(genre_id=self.genre.id),
            '/admin/artist/artist/',
            '/admin/artist/artist/add/',
            '/admin/artist/artist/{artist_id}/change/'.format(artist_id=self.artist.id),
        ]


class ArtistWebTestCase(PerDiemTestCase):

    def get200s(self):
        return [
            '/artists/',
            '/artists/?genre=Progressive+Rock',
            '/artists/?distance=50&lat=43.7689&lon=-79.4138',
            '/artists/?sort=recent',
            '/artists/?sort=funded',
            '/artists/?sort=time-remaining',
            '/artists/?sort=investors',
            '/artists/?sort=raised',
            '/artists/?sort=valuation',
            '/artist/apply/',
            '/artist/{slug}/'.format(slug=self.artist.slug),
            '/artist/{slug}/'.format(slug=self.artist_no_campaign.slug),
        ]

    def testArtistDetailPageUnauthenticated(self):
        self.client.logout()
        self.assertResponseRenders('/artist/{slug}/'.format(slug=self.artist.slug))

    @mock.patch('artist.views.Nominatim.geocode')
    def testGeocoderInArtistList(self, mock_geocode):
        url = '/artists/?distance=50&location=Toronto,%20ON'

        # First the Geocoder service fails and so we display warning to user
        mock_geocode.side_effect = GeocoderTimedOut
        response = self.assertResponseRenders(url)
        self.assertIn('Geocoding failed.', response.content)

        # Then the Geocoder service kicks back online and we succeed
        mock_geocode.side_effect = None
        mock_geocode.return_value = mock.Mock(latitude=43.653226, longitude=-79.383184)
        response = self.assertResponseRenders(url)
        self.assertNotIn('Geocoding failed.', response.content)

    def testArtistDoesNotExistReturns404(self):
        self.assertResponseRenders('/artist/does-not-exist/', status_code=404)

    def testArtistApplication(self):
        self.assertResponseRedirects(
            '/artist/apply/',
            '/artist/apply/thanks',
            method='POST',
            data={
                'artist_name': 'Segmentation Fault',
                'genre': 'Heavy Metal',
                'hometown': 'Waterloo, ON, Canada',
                'email': self.user.email,
                'phone_number': '(226) 123-4567',
                'bio': (
                    'We are a really cool heavy metal band. We mostly perform covers but are excited to '
                    'create an album, and we\'re hoping PerDiem can help us do that.'
                ),
                'campaign_reason': 'We want to record our next album: Access Granted.',
                'campaign_expenses': 'Studio time, mastering, mixing, etc.',
                'music_link': 'https://www.spotify.com/',
                'terms': True,
            }
        )
