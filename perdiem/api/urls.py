"""
:Created: 29 May 2016
:Author: Lucas Connors

"""

from django.conf.urls import url

from api.views import CoordinatesFromAddressView


urlpatterns = [
    url(r'^coordinates/?$', CoordinatesFromAddressView.as_view(), name='coordinates'),
]
