"""
:Created: 24 July 2016
:Author: Lucas Connors

"""

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


class MusicWebTestCase(PerDiemTestCase):

    def get200s(self):
        return [
            '/music/',
            '/artist/{artist_slug}/{album_slug}/'.format(
                artist_slug=self.artist.slug,
                album_slug=self.album.slug
            ),
        ]
