"""
:Created: 24 July 2016
:Author: Lucas Connors

"""

from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from music.models import Album


class AlbumDetailView(TemplateView):

    template_name = 'music/album_detail.html'

    def get_context_data(self, **kwargs):
        context = super(AlbumDetailView, self).get_context_data(**kwargs)
        artist_slug = kwargs['artist_slug']
        album_slug = kwargs['album_slug']
        context['album'] = get_object_or_404(Album, slug=album_slug, project__artist__slug=artist_slug)
        return context
