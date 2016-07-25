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
        ]


class MusicWebTestCase(PerDiemTestCase):

    def get200s(self):
        return [
            '/artist/{artist_slug}/{album_slug}/'.format(
                artist_slug=self.artist.slug,
                album_slug=self.album.slug
            ),
        ]
