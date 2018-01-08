"""
:Created: 24 July 2016
:Author: Lucas Connors

"""

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils import timezone

from campaign.models import Campaign
from music.factories import ActivityEstimateFactory, AlbumFactory, TrackFactory
from music.models import Album, ActivityEstimate
from perdiem.tests import PerDiemTestCase


class MusicModelsTestCase(TestCase):

    def testUnicodeOfAlbumIsAlbumName(self):
        album = AlbumFactory()
        self.assertEquals(unicode(album), album.name)

    def testUnicodeOfTrack(self):
        track = TrackFactory()
        self.assertEquals(
            unicode(track),
            "{album_name} #1: {track_name}".format(album_name=track.album.name, track_name=track.name)
        )

    def testUnicodeOfActivityEstimateIsContentObject(self):
        activity_estimate = ActivityEstimateFactory()
        self.assertEquals(unicode(activity_estimate), unicode(activity_estimate.content_object))


class MusicAdminWebTestCase(PerDiemTestCase):

    def get200s(self):
        return [
            '/admin/music/activityestimate/daily-report/',
        ]

    def testActivityEstimatesRequireCampaigns(self):
        album = AlbumFactory()
        response = self.assertResponseRenders(
            '/admin/music/activityestimate/add/',
            method='POST',
            data={
                'date': timezone.now().date(),
                'activity_type': ActivityEstimate.ACTIVITY_STREAM,
                'content_type': ContentType.objects.get_for_model(album).id,
                'object_id': album.id,
                'total': 10,
            },
            has_form_error=True
        )
        self.assertIn("You cannot create activity estimates without defining the revenue percentages", response.content)

    def testActivityEstimatesWhereAlbumDoesNotExist(self):
        invalid_album_id = Album.objects.count() + 1
        response = self.assertResponseRenders(
            '/admin/music/activityestimate/add/',
            method='POST',
            data={
                'date': timezone.now().date(),
                'activity_type': ActivityEstimate.ACTIVITY_STREAM,
                'content_type': ContentType.objects.get_for_model(Album).id,
                'object_id': invalid_album_id,
                'total': 10,
            },
            has_form_error=True
        )
        self.assertIn(
            "The album with ID {invalid_album_id} does not exist.".format(invalid_album_id=invalid_album_id),
            response.content
        )


class MusicWebTestCase(PerDiemTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.album = AlbumFactory()
        cls.artist = cls.album.project.artist

    def get200s(self):
        return [
            '/music/',
            '/artist/{artist_slug}/{album_slug}/'.format(
                artist_slug=self.artist.slug,
                album_slug=self.album.slug
            ),
        ]
