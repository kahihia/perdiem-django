"""
:Created: 12 March 2016
:Author: Lucas Connors

"""

from django.core.management import call_command
from django.utils import timezone

import factory
from geopy.exc import GeocoderTimedOut
import mock

from artist.factories import ArtistFactory, artistfactory_factory, updatefactory_factory
from artist.models import Playlist as PlaylistConst
from perdiem.tests import MigrationTestCase, PerDiemTestCase


class SetInitialUpdateTitlesMigrationTestCase(MigrationTestCase):

    migrate_from = '0005_auto_20160522_2328'
    migrate_to = '0006_updatetitles'

    def setUpBeforeMigration(self, apps):
        # Create an update
        UpdateFactoryForMigrationTestCase = updatefactory_factory(apps=apps)
        self.update = UpdateFactoryForMigrationTestCase()

    def testUpdatesHaveInitialTitles(self):
        today = timezone.now().strftime("%m/%d/%Y")
        self.update.refresh_from_db()
        self.assertEquals(self.update.title, "Artist 0 Update: {today}".format(today=today))


class SoundCloudPlaylistToPlaylistMigrationTestCase(MigrationTestCase):

    migrate_from = '0009_auto_20170201_0753'
    migrate_to = '0010_auto_20170201_0754'

    def setUpBeforeMigration(self, apps):
        class SoundCloudPlaylistFactoryForMigrationTestCase(factory.DjangoModelFactory):
            class Meta:
                model = apps.get_model('artist', 'SoundCloudPlaylist')
            artist = factory.SubFactory(artistfactory_factory(apps=apps))

        # Create a SoundCloudPlaylist
        self.soundcloudplaylist = SoundCloudPlaylistFactoryForMigrationTestCase()

    def testPlaylistURIIsFromSoundCloudPlaylist(self):
        Playlist = self.apps.get_model('artist', 'Playlist')
        playlist = Playlist.objects.get()
        self.assertEquals(playlist.provider, PlaylistConst.PLAYLIST_PROVIDER_SOUNDCLOUD)
        self.assertEquals(playlist.uri, self.soundcloudplaylist.playlist)


class ArtistWebTestCase(PerDiemTestCase):

    @classmethod
    def setUpTestData(cls):
        super(ArtistWebTestCase, cls).setUpTestData()
        cls.artist = ArtistFactory()

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
