"""
:Created: 19 March 2016
:Author: Lucas Connors

"""

import datetime

from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.http import (
    HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
)
from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from geopy.geocoders import Nominatim

from artist.forms import (
    CoordinatesFromAddressForm, ArtistApplyForm, ArtistUpdateForm
)
from artist.models import Genre, Artist, Update, UpdateImage, UpdateMediaURL
from emails.messages import ArtistApplyEmail


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


class ArtistListView(ListView):

    template_name = 'artist/artist_list.html'
    context_object_name = 'artists'

    ORDER_BY_NAME = {
        'recent': 'Recently Added',
        'funded': '% Funded',
        'time-remaining': 'Time to Go',
        'investors': '# Investors',
        'raised': 'Amount Raised',
        'valuation': 'Valuation',
    }

    def dispatch(self, request, *args, **kwargs):
        # Filtering
        self.active_genre = request.GET.get('genre', 'All')
        self.distance = request.GET.get('distance')
        self.location = request.GET.get('location')
        self.lat = request.GET.get('lat')
        self.lon = request.GET.get('lon')

        # Sorting
        order_by_slug = request.GET.get('sort')
        if order_by_slug not in self.ORDER_BY_NAME:
            order_by_slug = 'recent'
        self.order_by = {
            'slug': order_by_slug,
            'name': self.ORDER_BY_NAME[order_by_slug],
        }
        return super(ArtistListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ArtistListView, self).get_context_data(**kwargs)
        sort_options = [{'slug': s, 'name': n,} for s, n in self.ORDER_BY_NAME.iteritems()]
        context.update({
            'now': datetime.datetime.now(),
            'genres': Genre.objects.all().order_by('name').values_list('name', flat=True),
            'active_genre': self.active_genre,
            'distance': self.distance if (self.lat and self.lon) or self.location else None,
            'location': self.location,
            'lat': self.lat,
            'lon': self.lon,
            'sort_options': sorted(sort_options, key=lambda o: o['name']),
            'order_by': self.order_by,
        })
        return context

    def get_queryset(self):
        artists = Artist.objects.all()

        # Filter by genre
        if self.active_genre != 'All':
            artists = artists.filter(genres__name=self.active_genre)

        # Filter by location
        if self.distance and self.location:
            geolocator = Nominatim()
            location = geolocator.geocode(self.location)
            artists = artists.filter_by_location(distance=int(self.distance), lat=location.latitude, lon=location.longitude)
        elif self.distance and self.lat and self.lon:
            artists = artists.filter_by_location(distance=int(self.distance), lat=self.lat, lon=self.lon)

        # Sorting
        order_by_name = self.order_by['slug']
        if order_by_name == 'funded':
            ordered_artists = artists.order_by_percentage_funded()
        elif order_by_name == 'time-remaining':
            ordered_artists = artists.order_by_time_remaining()
        elif order_by_name == 'investors':
            ordered_artists = artists.annotate(
                num_investors=models.Count(
                    models.Case(
                        models.When(
                            campaign__investment__charge__paid=True,
                            then='campaign__investment__charge__customer__user'
                        )
                    ),
                    distinct=True
                )
            ).order_by('-num_investors')
        elif order_by_name == 'raised':
            ordered_artists = artists.annotate(
                amount_raised=models.Sum(
                    models.Case(
                        models.When(
                            campaign__investment__charge__paid=True,
                            then=models.F('campaign__investment__num_shares') * models.F('campaign__value_per_share'),
                        ),
                        default=0,
                        output_field=models.IntegerField()
                    )
                )
            ).order_by('-amount_raised')
        elif order_by_name == 'valuation':
            ordered_artists = artists.order_by_valuation()
        else:
            ordered_artists = artists.order_by('-id')

        return ordered_artists


class ArtistDetailView(FormView):

    template_name = 'artist/artist_detail.html'
    form_class = ArtistUpdateForm

    def get_success_url(self):
        return reverse('artist', kwargs={'slug': self.slug,})

    def has_permission_to_submit_update(self, user):
        return user.is_superuser or self.artist.artistadmin_set.filter(user=user).exists()

    def dispatch(self, request, *args, **kwargs):
        self.slug = kwargs['slug']
        self.artist = get_object_or_404(Artist, slug=self.slug)
        return super(ArtistDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(ArtistDetailView, self).get_context_data(*args, **kwargs)
        context['PINAX_STRIPE_PUBLIC_KEY'] = settings.PINAX_STRIPE_PUBLIC_KEY
        context['PERDIEM_FEE'] = settings.PERDIEM_FEE
        context['has_permission_to_submit_update'] = self.has_permission_to_submit_update(self.request.user)

        context['artist'] = self.artist
        campaign = self.artist.active_campaign()

        if campaign:
            context['campaign'] = campaign
            context['fans_percentage'] = campaign.fans_percentage
            investors = campaign.investors()
            context['investors'] = investors.values()

            if self.request.user.is_authenticated():
                user_investor = investors.get(self.request.user.id)
                if user_investor and user_investor['percentage'] >= 0.5:
                    context['fans_percentage'] -= user_investor['percentage']
                    context['user_investor'] = user_investor

        context['updates'] = self.artist.update_set.all().order_by('-created_datetime')

        return context

    def form_valid(self, form):
        d = form.cleaned_data

        # Verify that the user has permission
        if not self.has_permission_to_submit_update(self.request.user):
            return HttpResponseForbidden()

        # Create the base update
        update = Update.objects.create(artist=self.artist, title=d['title'], text=d['text'])

        # Attach images/videos to the update
        image = d['image']
        if image:
            UpdateImage.objects.create(update=update, img=image)
        image_url = d['image_url']
        if image_url:
            UpdateMediaURL.objects.create(update=update, media_type=UpdateMediaURL.MEDIA_IMAGE, url=image_url)
        youtube_url = d['youtube_url']
        if youtube_url:
            UpdateMediaURL.objects.create(update=update, media_type=UpdateMediaURL.MEDIA_YOUTUBE, url=youtube_url)

        return super(ArtistDetailView, self).form_valid(form)


class ArtistApplyFormView(FormView):

    template_name = 'artist/artist_application.html'
    form_class = ArtistApplyForm

    def get_success_url(self):
        return reverse('artist_application_thanks')

    def get_initial(self):
        initial = super(ArtistApplyFormView, self).get_initial()
        user = self.request.user
        if user.is_authenticated():
            initial['email'] = user.email
        return initial

    def form_valid(self, form):
        # Add user_id to context, if available
        context = form.cleaned_data
        user = self.request.user
        if user.is_authenticated():
            context['user_id'] = user.id

        # Send artist application email
        ArtistApplyEmail().send_to_email(email='info@investperdiem.com', context=context)

        return super(ArtistApplyFormView, self).form_valid(form)
