"""
:Created: 29 May 2016
:Author: Lucas Connors

"""

from django.contrib.auth.mixins import (
    LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
)
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.generic import View

from geopy.geocoders import Nominatim

from api.forms import CoordinatesFromAddressForm
from artist.models import Update


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
