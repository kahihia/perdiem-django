"""
:Created: 5 March 2016
:Author: Lucas Connors

"""

import datetime

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.text import slugify

from accounts.models import UserAvatar, UserAvatarURL
from artist.models import Genre, Artist, ArtistAdmin, Update
from campaign.models import Project, Campaign, RevenueReport
from music.models import Album, Track, ActivityEstimate
from pigeon.test import RenderTestCase


class PerDiemTestCase(RenderTestCase):

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

    @classmethod
    def setup_users(cls):
        cls.user = User.objects.create_user(
            cls.USER_USERNAME,
            email=cls.USER_EMAIL,
            password=cls.USER_PASSWORD
        )
        cls.user.is_staff = True
        cls.user.is_superuser = True
        cls.user.save()

        avatar = UserAvatar.objects.create(
            user=cls.user,
            provider=UserAvatar.PROVIDER_GOOGLE
        )
        UserAvatarURL.objects.create(avatar=avatar, url='')

        cls.ordinary_user = User.objects.create_user(
            cls.ORDINARY_USER_USERNAME,
            email=cls.ORDINARY_USER_EMAIL,
            password=cls.USER_PASSWORD
        )
        cls.manager_user = User.objects.create_user(
            cls.MANAGER_USER_USERNAME,
            email=cls.MANAGER_USER_EMAIL,
            password=cls.USER_PASSWORD
        )

    @classmethod
    def create_first_instances(cls):
        cls.genre = Genre.objects.create(name=cls.GENRE_NAME)
        cls.artist = Artist.objects.create(
            name=cls.ARTIST_NAME,
            slug=slugify(cls.ARTIST_NAME),
            lat=cls.ARTIST_LATITUDE,
            lon=cls.ARTIST_LONGITUDE,
            location=cls.ARTIST_LOCATION
        )
        cls.artist.genres.add(cls.genre)
        ArtistAdmin.objects.create(artist=cls.artist, user=cls.manager_user, role=ArtistAdmin.ROLE_MANAGER)
        cls.update = Update.objects.create(artist=cls.artist, text=cls.ARTIST_UPDATE)

        cls.project = Project.objects.create(
            artist=cls.artist,
            reason=cls.PROJECT_REASON
        )
        cls.campaign = Campaign.objects.create(
            project=cls.project,
            amount=cls.CAMPAIGN_AMOUNT,
            fans_percentage=cls.CAMPAIGN_FANS_PERCENTAGE,
            end_datetime=timezone.now() + datetime.timedelta(days=14)
        )
        cls.revenue_report = RevenueReport.objects.create(
            project=cls.project,
            amount=cls.PROJECT_REVENUE_REPORT_AMOUNT
        )
        cls.album = Album.objects.create(
            project=cls.project,
            name=cls.ALBUM_NAME,
            slug=slugify(cls.ALBUM_NAME)
        )
        for i, track_name in enumerate(cls.TRACK_NAMES, 1):
            Track.objects.create(
                album=cls.album,
                track_number=i,
                name=track_name,
                duration=datetime.timedelta(minutes=2)
            )
        cls.activity_estimate = ActivityEstimate.objects.create(
            activity_type='download',
            content_type=ContentType.objects.get_for_model(Album),
            object_id=cls.album.id,
            total=5
        )

        cls.artist_no_campaign = Artist.objects.create(
            name=cls.ARTIST_NO_CAMPAIGN_NAME,
            slug=slugify(cls.ARTIST_NO_CAMPAIGN_NAME),
            lat=cls.ARTIST_LATITUDE,
            lon=cls.ARTIST_LONGITUDE,
            location=cls.ARTIST_LOCATION
        )

    @classmethod
    def setUpTestData(cls):
        super(PerDiemTestCase, cls).setUpTestData()
        cls.setup_users()
        cls.create_first_instances()

    def setUp(self):
        self.client.login(username=self.USER_USERNAME, password=self.USER_PASSWORD)


class HealthCheckWebTestCase(RenderTestCase):

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


class ExtrasWebTestCase(RenderTestCase):

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
