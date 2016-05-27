"""
:Created: 5 April 2016
:Author: Lucas Connors

"""

from perdiem.tests import PerDiemTestCase


class PerDiemHomeWebTestCase(PerDiemTestCase):

    def get200s(self):
        return [
            '/',
            '/faq/',
            '/trust/',
            '/terms/',
            '/privacy/',
            '/contact/',
            '/resources/',
            '/accounts/register/',
            '/accounts/password/reset/',
            '/accounts/password/reset/0/0-0/',
            '/accounts/password/reset/complete/',
            '/profile/',
            '/profile/{username}/'.format(username=self.user.username),
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
            'login-password': self.USER_PASSWORD,
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
                'password1': self.USER_PASSWORD,
                'password2': self.USER_PASSWORD,
            }
        )

    def testInvalidProfilesAndAnonymousProfilesLookIdentical(self):
        # Set a user to invest anonymously
        self.ordinary_user.userprofile.invest_anonymously = True
        self.ordinary_user.userprofile.save()

        # Get HTML from an invalid profile
        invalid_profile_url = '/profile/does-not-exist/'
        invalid_profile_response = self.assertResponseRenders(
            invalid_profile_url,
            status_code=404
        )
        invalid_profile_html = invalid_profile_response.content.replace(invalid_profile_url, '')

        # Get HTML from an anonymous profile
        anonymous_profile_url = '/profile/{anonymous_username}/'.format(
            anonymous_username=self.ordinary_user.username
        )
        anonymous_profile_response = self.assertResponseRenders(
            anonymous_profile_url,
            status_code=404
        )
        anonymous_profile_html = anonymous_profile_response.content.replace(anonymous_profile_url, '')

        # Verify that the HTML from these two different pages are identical
        self.assertHTMLEqual(invalid_profile_html, anonymous_profile_html)

    def testEditName(self):
        self.assertResponseRenders(
            '/profile/',
            method='POST',
            data={
                'action': 'edit_name',
                'username': self.USER_USERNAME,
                'first_name': self.USER_FIRST_NAME,
                'last_name': self.USER_LAST_NAME,
                'invest_anonymously': False,
            }
        )

    def testEditAvatar(self):
        self.assertResponseRenders(
            '/profile/',
            method='POST',
            data={
                'action': 'edit_avatar',
                'avatar': self.user.userprofile.avatar,
            }
        )

    def testChangePassword(self):
        self.assertResponseRenders(
            '/profile/',
            method='POST',
            data={
                'action': 'change_password',
                'old_password': self.USER_PASSWORD,
                'new_password1': 'abc1234',
                'new_password2': 'abc1234',
            }
        )

    def testUpdateEmailPreferences(self):
        self.assertResponseRenders(
            '/profile/',
            method='POST',
            data={
                'action': 'email_preferences',
                'subscription_all': True,
                'subscription_news': False
            }
        )

    def testPasswordReset(self):
        self.client.logout()
        self.assertResponseRedirects(
            '/accounts/password/reset/',
            '/accounts/password/reset/sent',
            method='POST',
            data={'email': self.user.email,}
        )

    def testContact(self):
        self.assertResponseRedirects(
            '/contact/',
            '/contact/thanks',
            method='POST',
            data={'inquiry': 'General Inquiry', 'email': 'msmith@example.com', 'message': 'Hello World!',}
        )
