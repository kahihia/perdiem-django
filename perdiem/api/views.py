"""
:Created: 29 May 2016
:Author: Lucas Connors

"""

import decimal

from django.contrib.auth.mixins import (
    LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
)
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.generic import View

from geopy.geocoders import Nominatim
from pinax.stripe.actions import charges, customers
from stripe import CardError

from api.forms import CoordinatesFromAddressForm
from artist.models import Update
from campaign.forms import PaymentChargeForm
from campaign.models import Campaign, Investment


class CoordinatesFromAddressView(PermissionRequiredMixin, View):

    permission_required = 'artist.add_artist'
    raise_exception = True

    def get(self, request, *args, **kwargs):
        # Validate request
        form = CoordinatesFromAddressForm(request.GET)
        if not form.is_valid():
            return HttpResponseBadRequest(form.errors)
        address = form.cleaned_data['address']

        # Return lat/lon for address
        geolocator = Nominatim()
        location = geolocator.geocode(address)
        return JsonResponse({
            'latitude': float("{0:.4f}".format(location.latitude)),
            'longitude': float("{0:.4f}".format(location.longitude)),
        })


class PaymentChargeView(LoginRequiredMixin, View):

    def post(self, request, campaign_id, *args, **kwargs):
        # Validate request and campaign status
        try:
            campaign = Campaign.objects.get(id=campaign_id)
        except Campaign.DoesNotExist:
            return HttpResponseBadRequest("Campaign with ID {campaign_id} does not exist.".format(campaign_id=campaign_id))
        else:
            if not campaign.open():
                return HttpResponseBadRequest("This campaign is no longer accepting investments.")
        form = PaymentChargeForm(request.POST, campaign=campaign)
        if not form.is_valid():
            return HttpResponseBadRequest(unicode(form.errors))
        d = form.cleaned_data

        # Get card and customer
        card = d['card']
        customer = customers.get_customer_for_user(request.user)
        if not customer:
            customer = customers.create(request.user, card=card, plan=None, charge_immediately=False)

        # Create charge
        num_shares = d['num_shares']
        amount = decimal.Decimal(campaign.total(num_shares))
        try:
            charge = charges.create(amount=amount, customer=customer.stripe_id)
        except CardError as e:
            return HttpResponseBadRequest(e.message)
        Investment.objects.create(charge=charge, campaign=campaign, num_shares=num_shares)
        return HttpResponse(status=205)


class DeleteUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):

    raise_exception = True

    def test_func(self, *args, **kwargs):
        try:
            update = Update.objects.select_related('artist').get(id=self.kwargs['update_id'])
        except Update.DoesNotExist:
            return False
        return update.artist.has_permission_to_submit_update(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        Update.objects.get(id=self.kwargs['update_id']).delete()
        return HttpResponse(status=204)
