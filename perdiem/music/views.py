"""
:Created: 24 July 2016
:Author: Lucas Connors

"""

from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.views.generic.list import ListView

from campaign.models import Investment
from music.models import Album


class MusicListView(ListView):

    template_name = 'music/music.html'
    context_object_name = 'albums'
    model = Album


class AlbumDetailView(TemplateView):

    template_name = 'music/album_detail.html'

    def get_context_data(self, **kwargs):
        context = super(AlbumDetailView, self).get_context_data(**kwargs)
        user = self.request.user

        album = get_object_or_404(
            Album,
            slug=kwargs['album_slug'],
            project__artist__slug=kwargs['artist_slug']
        )
        user_is_investor = user.is_authenticated and Investment.objects.filter(campaign__project__album=album, charge__customer__user=user, charge__paid=True).exists()
        context.update({
            'album': album,
            'user_is_investor': user_is_investor,
        })

        return context
