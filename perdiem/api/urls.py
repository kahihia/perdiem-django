"""
:Created: 29 May 2016
:Author: Lucas Connors

"""

from django.conf.urls import url

from api.views import (
    CoordinatesFromAddressView, PaymentChargeView, DeleteUpdateView
)


urlpatterns = [
    url(r'^coordinates/?$', CoordinatesFromAddressView.as_view()),
    url(r'^payments/charge/(?P<campaign_id>\d+)/?$', PaymentChargeView.as_view(), name='pinax_stripe_charge'),
    url(r'^update/(?P<update_id>\d+)/?$', DeleteUpdateView.as_view()),
]
