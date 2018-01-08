"""
:Created: 5 April 2016
:Author: Lucas Connors

"""

import re

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.test import override_settings

import mock

from accounts.factories import UserAvatarFactory, UserFactory, userfactory_factory
from artist.factories import ArtistFactory
from campaign.factories import InvestmentFactory, ProjectFactory
from campaign.models import RevenueReport
from emails.models import VerifiedEmail
from perdiem.tests import MigrationTestCase, PerDiemTestCase


class CreateInitialUserProfilesMigrationTestCase(MigrationTestCase):

    migrate_from = '0001_initial'
    migrate_to = '0002_userprofiles'

    def setUpBeforeMigration(self, apps):
        # Create a user
        UserFactoryForMigrationTestCase = userfactory_factory(apps=apps, has_password=False)
        self.user = UserFactoryForMigrationTestCase()

    def testUsersHaveUserProfiles(self):
        UserProfile = self.apps.get_model('accounts', 'UserProfile')
        self.assertEquals(UserProfile.objects.get().user.id, self.user.id)


class UsernamesToLowercaseMigrationTestCase(MigrationTestCase):

    USERNAME = 'JSmith'

    migrate_from = '0004_auto_20160522_2139'
    migrate_to = '0005_auto_20160623_0657'

    def setUpBeforeMigration(self, apps):
        # Create a user with a username that has uppercase characters
        UserFactoryForMigrationTestCase = userfactory_factory(apps=apps, has_password=False)
        self.user = UserFactoryForMigrationTestCase(username=self.USERNAME)

    def testUsernamesAreLowercase(self):
        self.user.refresh_from_db()
        self.assertEquals(self.user.username, self.USERNAME.lower())


class AuthWebTestCase(PerDiemTestCase):

    def get200s(self):
        return [
            '/',
            '/accounts/register/',
            '/accounts/password/reset/',
            '/accounts/password/reset/0/0-0/',
            '/accounts/password/reset/complete/',
        ]

    def testHomePageUnauthenticated(self):
        self.client.logout()
        self.assertResponseRenders('/')

    def testLogout(self):
        self.assertResponseRedirects('/accounts/logout/', '/')

    def testLogin(self):
        self.client.logout()
        login_data = {
            'login-username': self.USER_USERNAME,
            'login-password': UserFactory._PASSWORD,
        }
        response = self.assertResponseRenders('/', method='POST', data=login_data)
        self.assertIn('LOGOUT', response.content)

    def testLoginWithUppercaseUsername(self):
        self.client.logout()
        login_data = {
            'login-username': self.USER_USERNAME.upper(),
            'login-password': UserFactory._PASSWORD,
        }
        response = self.assertResponseRenders('/', method='POST', data=login_data)
        self.assertIn('LOGOUT', response.content)

    def testRegister(self):
        self.client.logout()
        self.assertResponseRedirects(
            '/accounts/register/',
            '/profile',
            method='POST',
            data={
                'username': 'msmith',
                'email': 'msmith@example.com',
                'password1': UserFactory._PASSWORD,
                'password2': UserFactory._PASSWORD,
            }
        )

    def testRegisterUsernameMustBeLowercase(self):
        self.client.logout()
        self.assertResponseRenders(
            '/accounts/register/',
            method='POST',
            data={
                'username': 'Msmith',
                'email': 'msmith@example.com',
                'password1': UserFactory._PASSWORD,
                'password2': UserFactory._PASSWORD,
            },
            has_form_error=True
        )

    def testPasswordReset(self):
        self.client.logout()
        self.assertResponseRedirects(
            '/accounts/password/reset/',
            '/accounts/password/reset/sent',
            method='POST',
            data={'email': self.user.email}
        )


class OAuth2TestCase(PerDiemTestCase):

    @mock.patch('social_core.backends.google.BaseGoogleOAuth2API.user_data')
    @mock.patch('social_core.backends.oauth.BaseOAuth2.request_access_token')
    def testGoogleOAuth2Login(self, mock_request_access_token, mock_user_data):
        mock_request_access_token.return_value = {'access_token': 'abc123'}
        mock_user_data.return_value = {
            u'id_token': u'abc123',
            u'image': {
                u'url': u'https://lh4.googleusercontent.com/abc123/photo.jpg?sz=50',
                u'isDefault': False,
            },
            u'token_type': u'Bearer',
            u'birthday': u'0000-01-01',
            u'verified': False,
            u'id': u'1234',
            u'displayName': u'John Smith',
            u'name': {u'givenName': u'John', u'familyName': u'Smith'},
            u'language': u'en',
            u'access_token': u'ya29.abc123',
            u'gender': u'male',
            u'expires_in': 3600,
            u'emails': [{u'type': u'account', u'value': u'jsmith@example.com'}],
        }

        # Click on "Sign in with Google" button
        self.client.logout()
        allowed_hosts_w_google = settings.ALLOWED_HOSTS + ['accounts.google.com']
        with override_settings(ALLOWED_HOSTS=allowed_hosts_w_google):
            self.assertResponseRedirects(
                '/login/google-oauth2-login/',
                'https://accounts.google.com/o/oauth2/auth',
                status_code=404  # The actual page will fail since the client ID used in tests does not exist
            )

        # The user auths and consents
        # Google redirects to our redirect URI
        state = Session.objects.get().get_decoded()['google-oauth2-login_state']
        self.assertResponseRedirects(
            '/complete/google-oauth2-login/?state={state}&code=4/abc123&session_state={state}'.format(state=state),
            '/profile/'
        )


class ProfileWebTestCase(PerDiemTestCase):

    def get200s(self):
        return [
            '/profile/',
            '/profile/{username}/'.format(username=self.user.username),
        ]

    def testUserProfileContextCaches(self):
        # Request the profile context for a user
        self.user.userprofile.profile_context()

        # Verify that this user's profile context is in cache
        self.assertIn('profile_context-{pk}'.format(pk=self.user.userprofile.pk), cache)

        # Create a new RevenueReport
        # We cannot use a factory to generate the RevenueReport here
        # because we actually need the post_save signals to be made
        RevenueReport.objects.create(project=ProjectFactory(), amount=100)

        # Verify that the user profile context is no longer in cache
        self.assertNotIn('profile_context-{pk}'.format(pk=self.user.userprofile.pk), cache)

    def testUserProfileContextContainsInvestments(self):
        investment = InvestmentFactory()
        self.assertGreater(investment.charge.customer.user.userprofile.profile_context()['total_investments'], 0)

    def testInvalidProfilesAndAnonymousProfilesLookIdentical(self):
        # Create a user that will invest anonymously
        anonymous_user = UserFactory()
        anonymous_user.userprofile.invest_anonymously = True
        anonymous_user.userprofile.save()

        # Get HTML from an invalid profile
        invalid_profile_url = '/profile/does-not-exist/'
        invalid_profile_response = self.assertResponseRenders(
            invalid_profile_url,
            status_code=404
        )
        invalid_profile_html = invalid_profile_response.content.replace(invalid_profile_url, '')

        # Get HTML from an anonymous profile
        anonymous_profile_url = '/profile/{anonymous_username}/'.format(
            anonymous_username=anonymous_user.username
        )
        anonymous_profile_response = self.assertResponseRenders(
            anonymous_profile_url,
            status_code=404
        )
        anonymous_profile_html = anonymous_profile_response.content.replace(anonymous_profile_url, '')

        # Remove CSRF tokens from profiles
        csrf_regex = r'<input[^>]+csrfmiddlewaretoken[^>]+>'
        invalid_profile_html = re.sub(csrf_regex, '', invalid_profile_html)
        anonymous_profile_html = re.sub(csrf_regex, '', anonymous_profile_html)

        # Verify that the HTML from these two different pages are identical
        self.assertHTMLEqual(invalid_profile_html, anonymous_profile_html)

    def testRedirectToProfile(self):
        # Redirect to artist details
        artist = ArtistFactory()
        self.assertResponseRedirects(
            '/{artist_slug}/'.format(artist_slug=artist.slug),
            '/artist/{artist_slug}'.format(artist_slug=artist.slug)
        )

        # Redirect to user's public profile
        self.assertResponseRedirects(
            '/{username}/'.format(username=self.user.username),
            '/profile/{username}'.format(username=self.user.username)
        )

        # Create a new user that matches the artist slug
        user_with_artist_username = UserFactory(username=artist.slug)

        # We still redirect to the artist details
        self.assertResponseRedirects(
            '/{username}/'.format(username=user_with_artist_username.username),
            '/artist/{artist_slug}'.format(artist_slug=artist.slug)
        )

    def testRedirectToProfileDoesNotExistReturns404(self):
        self.assertResponseRenders('/does-not-exist/', status_code=404)


class SettingsWebTestCase(PerDiemTestCase):

    def get200s(self):
        return [
            '/accounts/settings/',
        ]

    def testEditUsernameMustBeLowercase(self):
        self.assertResponseRenders(
            '/accounts/settings/',
            method='POST',
            data={
                'action': 'edit_name',
                'username': self.USER_USERNAME.upper(),
                'invest_anonymously': False,
            },
            has_form_error=True
        )

    def testEditName(self):
        self.assertResponseRenders(
            '/accounts/settings/',
            method='POST',
            data={
                'action': 'edit_name',
                'username': self.USER_USERNAME,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'invest_anonymously': False,
            }
        )

    def testEditAvatar(self):
        user_avatar = UserAvatarFactory(user=self.user)
        self.assertResponseRenders(
            '/accounts/settings/',
            method='POST',
            data={
                'action': 'edit_avatar',
                'avatar': user_avatar.id,
            }
        )

    def testChangePassword(self):
        self.assertResponseRenders(
            '/accounts/settings/',
            method='POST',
            data={
                'action': 'change_password',
                'old_password': UserFactory._PASSWORD,
                'new_password1': 'abc1234',
                'new_password2': 'abc1234',
            }
        )

    @mock.patch('emails.mailchimp.requests.put')
    @override_settings(MAILCHIMP_API_KEY='FAKE_API_KEY', MAILCHIMP_LIST_ID='FAKE_LIST_ID')
    def testUpdateEmailPreferences(self, mock_mailchimp_request):
        mock_mailchimp_request.return_value = mock.Mock(status_code=200)

        self.assertResponseRenders(
            '/accounts/settings/',
            method='POST',
            data={
                'action': 'email_preferences',
                'email': self.user.email,
                'subscription_all': True,
                'subscription_news': False,
                'subscription_artist_update': True,
            }
        )

    @mock.patch('emails.mailchimp.requests.put')
    @override_settings(MAILCHIMP_API_KEY='FAKE_API_KEY', MAILCHIMP_LIST_ID='FAKE_LIST_ID')
    def testUpdateEmailAddress(self, mock_mailchimp_request):
        mock_mailchimp_request.return_value = mock.Mock(status_code=200)

        # Verify first email
        verified_email = VerifiedEmail.objects.get_current_email(self.user)
        verified_email.verified = True
        verified_email.save()

        # Update email address to something new
        self.assertResponseRenders(
            '/accounts/settings/',
            method='POST',
            data={
                'action': 'email_preferences',
                'email': 'newemail@example.com',
            }
        )

        # Check that new email is not verified
        self.user = User.objects.get(id=self.user.id)
        self.assertFalse(VerifiedEmail.objects.is_current_email_verified(self.user))

    def testCannotChangeEmailToExistingAccount(self):
        other_user = UserFactory()
        self.assertResponseRenders(
            '/accounts/settings/',
            method='POST',
            data={
                'action': 'email_preferences',
                'email': other_user.email,
            },
            has_form_error=True
        )
