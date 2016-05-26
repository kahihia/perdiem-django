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
