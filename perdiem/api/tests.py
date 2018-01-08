"""
:Created: 29 May 2016
:Author: Lucas Connors

"""

import mock

from geopy.exc import GeocoderTimedOut

from perdiem.tests import PerDiemTestCase
from accounts.factories import UserFactory
from artist.factories import ArtistAdminFactory, UpdateFactory
from campaign.factories import CampaignFactory


class CoordinatesFromAddressTestCase(PerDiemTestCase):

    url = '/api/coordinates/?address={address}'
    valid_url = url.format(address='Willowdale%2C+Toronto%2C+Ontario%2C+Canada')

    @mock.patch('api.views.Nominatim.geocode')
    def testCoordinatesFromAddress(self, mock_geocode):
        # First the Geocoder service fails and so we return 503
        mock_geocode.side_effect = GeocoderTimedOut
        self.assertAPIResponseRenders(self.valid_url, status_code=503)

        # Then the Geocoder service kicks back online and we succeed
        mock_geocode.side_effect = None
        mock_geocode.return_value = mock.Mock(latitude=43.766751, longitude=-79.410332)
        response = self.assertAPIResponseRenders(self.valid_url)
        lat, lon = response['latitude'], response['longitude']
        self.assertEquals(lat, 43.7668)
        self.assertEquals(lon, -79.4103)

    def testCoordinatesFromAddressRequiresAddress(self):
        for url in ['/api/coordinates/', self.url.format(address='')]:
            self.assertAPIResponseRenders(url, status_code=400)

    def testCoordinatesFromAddressFailsWithoutPermission(self):
        # Logout from being a superuser
        self.client.logout()

        # Coordinates from Address API requires permission
        # but you're not authenticated
        self.assertResponseRenders(self.valid_url, status_code=403)

        # Login as an ordinary user
        ordinary_user = UserFactory()
        self.client.login(
            username=ordinary_user.username,
            password=UserFactory._PASSWORD
        )

        # Coordinates from Address API requires permission
        # but you don't have the required permission
        self.assertResponseRenders(self.valid_url, status_code=403)


class PaymentChargeTestCase(PerDiemTestCase):

    @mock.patch('pinax.stripe.webhooks.Webhook.validate')
    @mock.patch('pinax.stripe.views.Webhook.extract_json')
    @mock.patch('stripe.Charge.create')
    @mock.patch('stripe.Customer.create')
    def testUserInvests(
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

        # Create campaign
        campaign = CampaignFactory()

        # User sends payment to Stripe
        self.assertResponseRenders('/artist/{slug}/'.format(slug=campaign.project.artist.slug))
        self.assertAPIResponseRenders(
            '/api/payments/charge/{campaign_id}/'.format(campaign_id=campaign.id),
            status_code=205,
            method='POST',
            data={'card': 'tok_6WqQnRecbRRrqvrdT1XXGP1d', 'num_shares': 1}
        )

        # Then Stripe responds confirming that the payment succeeded
        self.assertResponseRenders('/payments/webhook/', method='POST')


class DeleteUpdateTestCase(PerDiemTestCase):

    url = '/api/update/{update_id}/'

    def setUp(self):
        super(DeleteUpdateTestCase, self).setUp()
        self.update = UpdateFactory()
        self.valid_url = self.url.format(update_id=self.update.id)

    def testDeleteUpdate(self):
        self.assertAPIResponseRenders(self.valid_url, status_code=204, method='DELETE')

    def testDeleteUpdateRequiresValidUpdateId(self):
        self.assertResponseRenders(self.url.format(update_id=0), status_code=403)

    def testDeleteUpdateFailsWithoutPermission(self):
        # Logout from being a superuser
        self.client.logout()

        # Delete Update API requires permission
        # but you're not authenticated
        self.assertResponseRenders(self.valid_url, status_code=403, method='DELETE')

        # Login as ordinary user
        ordinary_user = UserFactory()
        self.client.login(
            username=ordinary_user.username,
            password=UserFactory._PASSWORD
        )

        # Delete Update API the user to be an ArtistAdmin (or superuser)
        # but you don't have access
        self.assertResponseRenders(self.valid_url, status_code=403)

    def testDeleteUpdateOnlyAllowsArtistAdminsToUpdateTheirArtists(self):
        # Logout from being a superuser
        self.client.logout()

        # Make the manager an ArtistAdmin
        manager_username = 'manager'
        ArtistAdminFactory(artist=self.update.artist, user__username=manager_username)

        # Login as manager
        self.client.login(username=manager_username, password=UserFactory._PASSWORD)

        # Delete Update API allows ArtistAdmins to update
        self.assertResponseRenders(self.valid_url, status_code=204, method='DELETE')

        # Delete Update API does not allow ArtistAdmins
        # to update artists they don't belong to
        update = UpdateFactory()
        self.assertResponseRenders(self.url.format(update_id=update.id), status_code=403, method='DELETE')
