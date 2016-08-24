"""
:Created: 26 July 2015
:Author: Lucas Connors

"""

from django.conf.urls import url
from django.contrib.auth.views import (
    logout, password_reset, password_reset_done, password_reset_confirm, password_reset_complete
)
from django.views.generic import TemplateView

from accounts.views import RegisterAccountView, SettingsView


urlpatterns = [
    url(r'^logout/?$', logout, {'next_page': '/',}, name='logout'),
    url(r'^register/?$', RegisterAccountView.as_view(), name='register'),
    url(r'^settings/?$', SettingsView.as_view(), name='settings'),

    url(r'^password/reset/sent/?$', password_reset_done, name='password_reset_done'),
    url(r'^password/reset/complete/?$', password_reset_complete, name='password_reset_complete'),
    url(
        r'^password/reset/(?P<uidb64>[0-9A-Za-z_-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/?$',
        password_reset_confirm,
        name='password_reset_confirm'
    ),
    url(r'^password/reset/?$', password_reset, name='password_reset'),

    url(
        r'^error/email-required/?$',
        TemplateView.as_view(template_name='registration/error/email-required.html'),
        name='error_email_required'
    ),
    url(
        r'^error/account-exists/?$',
        TemplateView.as_view(template_name='registration/error/account-exists.html'),
        name='error_account_exists'
    ),
    url(
        r'^error/account-does-not-exist/?$',
        TemplateView.as_view(template_name='registration/error/account-does-not-exist.html'),
        name='error_account_does_not_exist'
    ),
]
