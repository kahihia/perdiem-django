"""
:Created: 5 March 2016
:Author: Lucas Connors

"""

import datetime
import json
import urllib
import urlparse

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify

from rest_framework import status

from accounts.models import UserAvatar, UserAvatarURL
from artist.models import Genre, Artist, ArtistAdmin, Update
from campaign.models import Project, Campaign, RevenueReport
from music.models import Album, Track, ActivityEstimate


class PerDiemTestCase(TestCase):

    USER_USERNAME = 'jsmith'
    USER_FIRST_NAME = 'John'
    USER_LAST_NAME = 'Smith'
    USER_EMAIL = 'jsmith@example.com'
    USER_PASSWORD = 'abc123'
    ORDINARY_USER_USERNAME = 'jdoe'
    ORDINARY_USER_EMAIL = 'jdoe@example.com'
    MANAGER_USER_USERNAME = 'manager'
    MANAGER_USER_EMAIL = 'manager@example.com'

    GENRE_NAME = 'Progressive Rock'
    ARTIST_NAME = 'Rush'
    ARTIST_LATITUDE = 43.7689
    ARTIST_LONGITUDE = -79.4138
    ARTIST_LOCATION = 'Willowdale, Toronto, Ontario, Canada'
    ARTIST_UPDATE = 'North American Tour This Year!'
    ARTIST_NO_CAMPAIGN_NAME = 'Scale the Summit'

    PROJECT_REASON = 'to record a new album'
    CAMPAIGN_AMOUNT = 10000
    CAMPAIGN_FANS_PERCENTAGE = 20
    PROJECT_REVENUE_REPORT_AMOUNT = 500
    ALBUM_NAME = 'Moving Pictures'
    TRACK_NAMES = ('Tom Sawyer', 'Red Barchetta',)

    @staticmethod
    def strip_query_params(url):
        return url.split('?')[0]

    @staticmethod
    def add_params_to_url(url, params):
        url_parts = list(urlparse.urlparse(url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = urllib.urlencode(query)
        return urlparse.urlunparse(url_parts)

    def assertResponseRenders(self, url, status_code=200, method='GET', data={}, has_form_error=False, **kwargs):
        request_method = getattr(self.client, method.lower())
        follow = status_code == 302
        response = request_method(url, data=data, follow=follow, **kwargs)

        if status_code == 302:
            redirect_url, response_status_code = response.redirect_chain[0]
        else:
            response_status_code = response.status_code
        self.assertEquals(
            response_status_code,
            status_code,
            "URL {url} returned with status code {actual_status} when {expected_status} was expected.".format(
                url=url,
                actual_status=response_status_code,
                expected_status=status_code
            )
        )

        # Check that forms submitted did not return errors (or did if it should have)
        form_error_assertion_method = self.assertIn if has_form_error else self.assertNotIn
        form_error_assertion_method('errorlist', response.content)

        return response

    def assertAPIResponseRenders(self, url, status_code=200, method='GET', data={}, **kwargs):
        api_url = self.add_params_to_url(url, {'format': 'json'})
        if data:
            data = json.dumps(data)
        response = self.assertResponseRenders(
            api_url,
            status_code=status_code,
            method=method,
            data=data,
            content_type='application/json',
            **kwargs
        )
        if status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_205_RESET_CONTENT]:
            return response
        return response.json()

    def assertResponseRedirects(self, url, redirect_url, status_code=200, method='GET', data={}, **kwargs):
        response = self.assertResponseRenders(url, status_code=302, method=method, data=data, **kwargs)
        redirect_url_from_response, _ = response.redirect_chain[0]
        self.assertEquals(self.strip_query_params(redirect_url_from_response), redirect_url)
        self.assertEquals(response.status_code, status_code)

    def get200s(self):
        return []

    def setup_users(self):
        self.user = User.objects.create_user(
            self.USER_USERNAME,
            email=self.USER_EMAIL,
            password=self.USER_PASSWORD
        )
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.client.login(
            username=self.USER_USERNAME,
            password=self.USER_PASSWORD
        )
        avatar = UserAvatar.objects.create(
            user=self.user,
            provider=UserAvatar.PROVIDER_GOOGLE
        )
        UserAvatarURL.objects.create(avatar=avatar, url='')

        self.ordinary_user = User.objects.create_user(
            self.ORDINARY_USER_USERNAME,
            email=self.ORDINARY_USER_EMAIL,
            password=self.USER_PASSWORD
        )
        self.manager_user = User.objects.create_user(
            self.MANAGER_USER_USERNAME,
            email=self.MANAGER_USER_EMAIL,
            password=self.USER_PASSWORD
        )

    def create_first_instances(self):
        self.genre = Genre.objects.create(name=self.GENRE_NAME)
        self.artist = Artist.objects.create(
            name=self.ARTIST_NAME,
            slug=slugify(self.ARTIST_NAME),
            lat=self.ARTIST_LATITUDE,
            lon=self.ARTIST_LONGITUDE,
            location=self.ARTIST_LOCATION
        )
        self.artist.genres.add(self.genre)
        ArtistAdmin.objects.create(artist=self.artist, user=self.manager_user, role=ArtistAdmin.ROLE_MANAGER)
        self.update = Update.objects.create(artist=self.artist, text=self.ARTIST_UPDATE)

        self.project = Project.objects.create(
            artist=self.artist,
            reason=self.PROJECT_REASON
        )
        self.campaign = Campaign.objects.create(
            project=self.project,
            amount=self.CAMPAIGN_AMOUNT,
            fans_percentage=self.CAMPAIGN_FANS_PERCENTAGE,
            end_datetime=timezone.now() + datetime.timedelta(days=14)
        )
        self.revenue_report = RevenueReport.objects.create(
            project=self.project,
            amount=self.PROJECT_REVENUE_REPORT_AMOUNT
        )
        self.album = Album.objects.create(
            project=self.project,
            name=self.ALBUM_NAME,
            slug=slugify(self.ALBUM_NAME)
        )
        for i, track_name in enumerate(self.TRACK_NAMES, 1):
            Track.objects.create(
                album=self.album,
                track_number=i,
                name=track_name,
                duration=datetime.timedelta(minutes=2)
            )
        self.activity_estimate = ActivityEstimate.objects.create(
            activity_type='download',
            content_type=ContentType.objects.get_for_model(Album),
            object_id=self.album.id,
            total=5
        )

        self.artist_no_campaign = Artist.objects.create(
            name=self.ARTIST_NO_CAMPAIGN_NAME,
            slug=slugify(self.ARTIST_NO_CAMPAIGN_NAME),
            lat=self.ARTIST_LATITUDE,
            lon=self.ARTIST_LONGITUDE,
            location=self.ARTIST_LOCATION
        )

    def setUp(self):
        super(PerDiemTestCase, self).setUp()
        self.setup_users()
        self.create_first_instances()

    def tearDown(self):
        RevenueReport.objects.all().delete()
        Campaign.objects.all().delete()
        Update.objects.all().delete()
        Artist.objects.all().delete()
        Genre.objects.all().delete()
        User.objects.all().delete()
        super(PerDiemTestCase, self).tearDown()

    def testRender200s(self):
        for url in self.get200s():
            self.assertResponseRenders(url)


class HealthCheckWebTestCase(PerDiemTestCase):

    def get200s(self):
        return [
            '/health-check/',
        ]


class AdminWebTestCase(PerDiemTestCase):

    def get200s(self):
        return [
            '/admin/',
        ]

    def testAdminLoginPageRenders(self):
        self.client.logout()
        self.assertResponseRedirects('/admin/', '/admin/login/')


class ExtrasWebTestCase(PerDiemTestCase):

    def get200s(self):
        return [
            '/faq/',
            '/trust/',
            '/terms/',
            '/privacy/',
            '/contact/',
            '/resources/',
        ]

    def testContact(self):
        self.assertResponseRedirects(
            '/contact/',
            '/contact/thanks',
            method='POST',
            data={'inquiry': 'General Inquiry', 'email': 'msmith@example.com', 'message': 'Hello World!'}
        )
