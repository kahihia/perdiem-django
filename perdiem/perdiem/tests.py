"""
:Created: 5 March 2016
:Author: Lucas Connors

"""

import datetime
import mock

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

    @mock.patch('pinax.stripe.webhooks.Webhook.validate')
    @mock.patch('pinax.stripe.views.Webhook.extract_json')
    @mock.patch('stripe.Charge.create')
    @mock.patch('stripe.Customer.create')
    def user_invests(
        self,
        mock_stripe_customer_create,
        mock_stripe_charge_create,
        mock_pinax_stripe_webhook_extract_json,
        mock_pinax_stripe_webhook_validate
    ):
        # Mock responses from Stripe
        mock_stripe_customer_create.return_value = {
            'account_balance': 0,
            'business_vat_id': None,
            'created': 1462665000,
            'currency': None,
            'default_source': 'card_2CXngrrA798I5wA01wQ74iTR',
            'delinquent': False,
            'description': None,
            'discount': None,
            'email': self.USER_EMAIL,
            'id': 'cus_2Pc8xEoaTAnVKr',
            'livemode': False,
            'metadata': {},
            'object': 'customer',
            'shipping': None,
            'sources': {
                'data': [
                    {
                        'address_city': None,
                        'address_country': None,
                        'address_line1': None,
                        'address_line1_check': None,
                        'address_line2': None,
                        'address_state': None,
                        'address_zip': None,
                        'address_zip_check': None,
                        'brand': 'Visa',
                        'country': 'US',
                        'customer': 'cus_2Pc8xEoaTAnVKr',
                        'cvc_check': 'pass',
                        'dynamic_last4': None,
                        'exp_month': 5,
                        'exp_year': 2019,
                        'fingerprint': 'Lq9DFkUmxf7xWHkn',
                        'funding': 'credit',
                        'id': 'card_2CXngrrA798I5wA01wQ74iTR',
                        'last4': '4242',
                        'metadata': {},
                        'name': self.USER_EMAIL,
                        'object': 'card',
                        'tokenization_method': None,
                    },
                ],
                'has_more': False,
                'object': 'list',
                'total_count': 1,
                'url': '/v1/customers/cus_2Pc8xEoaTAnVKr/sources',
            },
            'subscriptions': {
                'data': [],
                'has_more': False,
                'object': 'list',
                'total_count': 0,
                'url': '/v1/customers/cus_2Pc8xEoaTAnVKr/subscriptions',
            },
        }
        mock_stripe_charge_create.return_value = {
            'amount': 235,
            'amount_refunded': 0,
            'application_fee': None,
            'balance_transaction': 'txn_Sazj9jMCau62PxJhOLzBXM3p',
            'captured': True,
            'created': 1462665010,
            'currency': 'usd',
            'customer': 'cus_2Pc8xEoaTAnVKr',
            'description': None,
            'destination': None,
            'dispute': None,
            'failure_code': None,
            'failure_message': None,
            'fraud_details': {},
            'id': 'ch_Upra88VQlJJPd0JxeTM0ZvHv',
            'invoice': None,
            'livemode': False,
            'metadata': {},
            'object': 'charge',
            'order': None,
            'paid': True,
            'receipt_email': None,
            'receipt_number': None,
            'refunded': False,
            'refunds': {
                'data': [],
                'has_more': False,
                'object': 'list',
                'total_count': 0,
                'url': '/v1/charges/ch_Upra88VQlJJPd0JxeTM0ZvHv/refunds',
            },
            'shipping': None,
            'source': {
                'address_city': None,
                'address_country': None,
                'address_line1': None,
                'address_line1_check': None,
                'address_line2': None,
                'address_state': None,
                'address_zip': None,
                'address_zip_check': None,
                'brand': 'Visa',
                'country': 'US',
                'customer': 'cus_2Pc8xEoaTAnVKr',
                'cvc_check': None,
                'dynamic_last4': None,
                'exp_month': 5,
                'exp_year': 2019,
                'fingerprint': 'Lq9DFkUmxf7xWHkn',
                'funding': 'credit',
                'id': 'card_2CXngrrA798I5wA01wQ74iTR',
                'last4': '4242',
                'metadata': {},
                'name': self.USER_EMAIL,
                'object': 'card',
                'tokenization_method': None,
            },
            'source_transfer': None,
            'statement_descriptor': None,
            'status': 'succeeded',
        }
        mock_pinax_stripe_webhook_extract_json.return_value = {
            'id': 'evt_t00Xx8V4jXhLUbUGPbpUkJlk',
            'object': 'event',
            'api_version': '2015-09-08',
            'created': 1462665020,
            'livemode': False,
            'pending_webhooks': 1,
            'request': 'req_x74Pcl1YdSdR67',
            'type': 'charge.succeeded',
            'data': {
                'object': {
                    'application_fee': None,
                    'livemode': False,
                    'currency': 'usd',
                    'invoice': None,
                    'fraud_details': {},
                    'id': 'ch_Upra88VQlJJPd0JxeTM0ZvHv',
                    'captured': True,
                    'receipt_number': None,
                    'destination': None,
                    'statement_descriptor': None,
                    'source': {
                        'address_state': None,
                        'last4': '4242',
                        'dynamic_last4': None,
                        'address_zip_check': None,
                        'address_country': None,
                        'id': 'card_2CXngrrA798I5wA01wQ74iTR',
                        'address_line2': None,
                        'address_line1': None,
                        'funding': 'credit',
                        'metadata': {},
                        'cvc_check': 'pass',
                        'exp_month': 5,
                        'tokenization_method': None,
                        'address_line1_check': None,
                        'brand': 'Visa',
                        'object': 'card',
                        'fingerprint': 'Lq9DFkUmxf7xWHkn',
                        'exp_year': 2019,
                        'address_zip': None,
                        'customer': 'cus_2Pc8xEoaTAnVKr',
                        'address_city': None,
                        'name': self.USER_EMAIL,
                        'country': 'US',
                    },
                    'balance_transaction': 'txn_Sazj9jMCau62PxJhOLzBXM3p',
                    'source_transfer': None,
                    'receipt_email': None,
                    'metadata': {},
                    'status': 'succeeded',
                    'amount_refunded': 0,
                    'description': None,
                    'refunded': False,
                    'object': 'charge',
                    'paid': True,
                    'failure_code': None,
                    'customer': 'cus_2Pc8xEoaTAnVKr',
                    'refunds': {
                        'has_more': False,
                        'total_count': 0,
                        'object': 'list',
                        'data': [],
                        'url': '/v1/charges/ch_Upra88VQlJJPd0JxeTM0ZvHv/refunds',
                    },
                    'created': 1462665020,
                    'failure_message': None,
                    'shipping': None,
                    'amount': 235,
                    'dispute': None,
                    'order': None,
                },
            },
        }

        # User sends payment to Stripe
        self.assertResponseRenders('/artist/{slug}/'.format(slug=self.artist.slug))
        self.assertAPIResponseRenders(
            '/api/payments/charge/{campaign_id}/'.format(campaign_id=self.campaign.id),
            status_code=205,
            method='POST',
            data={'card': 'tok_6WqQnRecbRRrqvrdT1XXGP1d', 'num_shares': 1}
        )

        # Then Stripe responds confirming that the payment succeeded
        self.assertResponseRenders('/payments/webhook/', method='POST')

    @classmethod
    def setUpTestData(cls):
        super(PerDiemTestCase, cls).setUpTestData()
        cls.setup_users()
        cls.create_first_instances()

    def setUp(self):
        self.client.login(username=self.USER_USERNAME, password=self.USER_PASSWORD)
        self.user_invests()


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
