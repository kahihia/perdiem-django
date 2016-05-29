"""
:Created: 29 May 2016
:Author: Lucas Connors

"""

from django.conf.urls import url

from api.views import CoordinatesFromAddressView, DeleteUpdateView


urlpatterns = [
    url(r'^coordinates/?$', CoordinatesFromAddressView.as_view()),
    url(r'^update/(?P<update_id>\d+)/?$', DeleteUpdateView.as_view()),
]
