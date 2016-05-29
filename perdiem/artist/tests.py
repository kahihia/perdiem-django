"""
:Created: 12 March 2016
:Author: Lucas Connors

"""

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
            '/artists/?distance=50&lat=43.7689&lon=-79.4138',
            '/artists/?distance=50&location=Toronto,%20ON',
            '/artists/?sort=recent',
            '/artists/?sort=funded',
            '/artist/apply/',
            '/artist/{slug}/'.format(slug=self.artist.slug),
            '/artist/{slug}/'.format(slug=self.artist_no_campaign.slug),
        ]

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
                'bio': 'We are a really cool heavy metal band. We mostly perform covers but are excited to create an album, and we\'re hoping PerDiem can help us do that.',
                'campaign_reason': 'We want to record our next album: Access Granted.',
                'campaign_expenses': 'Studio time, mastering, mixing, etc.',
                'music_link': 'https://www.spotify.com/',
                'terms': True,
            }
        )
