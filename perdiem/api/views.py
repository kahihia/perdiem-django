"""
:Created: 29 May 2016
:Author: Lucas Connors

"""

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.generic import View

from geopy.geocoders import Nominatim

from api.forms import CoordinatesFromAddressForm


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
