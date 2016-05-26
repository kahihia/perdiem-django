"""
:Created: 26 July 2015
:Author: Lucas Connors

"""

from django.conf.urls import url
from django.contrib.auth.views import (
    logout, password_reset, password_reset_done, password_reset_confirm,
    password_reset_complete
)

from accounts.views import RegisterAccountView


urlpatterns = [
    url(r'^logout/?$', logout, {'next_page': '/',}, name='logout'),
    url(r'^register/?$', RegisterAccountView.as_view(), name='register'),
    url(r'^password/reset/sent/?$', password_reset_done, name='password_reset_done'),
    url(r'^password/reset/complete/?$', password_reset_complete, name='password_reset_complete'),
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z_-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/?$', password_reset_confirm, name='password_reset_confirm'),
    url(r'^password/reset/?$', password_reset, name='password_reset'),
]
