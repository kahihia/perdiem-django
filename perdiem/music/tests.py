"""
:Created: 24 July 2016
:Author: Lucas Connors

"""

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from campaign.models import Campaign
from music.models import ActivityEstimate
from perdiem.tests import PerDiemTestCase


class MusicAdminWebTestCase(PerDiemTestCase):

    def get200s(self):
        return [
            '/admin/music/',
            '/admin/music/album/',
            '/admin/music/album/add/',
            '/admin/music/album/{album_id}/change/'.format(album_id=self.album.id),
            '/admin/music/track/',
            '/admin/music/track/add/',
            '/admin/music/track/{track_id}/change/'.format(track_id=self.album.track_set.all()[0].id),
            '/admin/music/activityestimate/',
            '/admin/music/activityestimate/add/',
            '/admin/music/activityestimate/{activity_estimate_id}/change/'.format(
                activity_estimate_id=self.activity_estimate.id
            ),
        ]

    def testActivityEstimatesRequireCampaigns(self):
        Campaign.objects.all().delete()
        response = self.assertResponseRenders(
            '/admin/music/activityestimate/add/',
            method='POST',
            data={
                'date': timezone.now().date(),
                'activity_type': ActivityEstimate.ACTIVITY_STREAM,
                'content_type': ContentType.objects.get_for_model(self.album).id,
                'object_id': self.album.id,
                'total': 10,
            },
            has_form_error=True
        )
        self.assertIn("You cannot create activity estimates without defining the revenue percentages", response.content)


class MusicWebTestCase(PerDiemTestCase):

    def get200s(self):
        return [
            '/music/',
            '/artist/{artist_slug}/{album_slug}/'.format(
                artist_slug=self.artist.slug,
                album_slug=self.album.slug
            ),
        ]
