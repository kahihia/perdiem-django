"""
:Created: 24 July 2016
:Author: Lucas Connors

"""

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.views.generic.list import ListView

from campaign.models import Investment
from music.models import Album, Track, ActivityEstimate


class MusicListView(ListView):

    template_name = 'music/music.html'
    context_object_name = 'albums'
    model = Album


class AlbumDetailView(TemplateView):

    template_name = 'music/album_detail.html'

    @staticmethod
    def generate_cumulative_revenue(revenue):
        artist_revenue_so_far = investor_revenue_so_far = 0
        for month in revenue:
            month['artist_revenue'] += artist_revenue_so_far
            month['investor_revenue'] += investor_revenue_so_far
            artist_revenue_so_far = month['artist_revenue']
            investor_revenue_so_far = month['investor_revenue']
        return revenue

    def get_revenue_from_activity(self, activity_qs, month, revenue_per_activity, multiplier=1):
        activity_per_month = activity_qs.annotate(total=models.Sum('total'))
        try:
            activity = activity_per_month.get(month=month)
        except ActivityEstimate.DoesNotExist:
            revenue = 0
        else:
            revenue = activity['total'] * multiplier * revenue_per_activity
        return revenue

    def estimated_revenue_month(self, month):
        tracks = self.album.track_set.all()
        track_ids = tracks.values_list('id', flat=True)
        num_tracks = tracks.count()

        # Determine revenue generated from downloads
        album_download_activity = self.download_activity.filter(
            content_type=ContentType.objects.get_for_model(Album),
            object_id=self.album.id
        )
        album_download_revenue = self.get_revenue_from_activity(
            album_download_activity,
            month=month,
            revenue_per_activity=settings.ESTIMATED_REVENUE_PER_DOWNLOAD,
            multiplier=num_tracks
        )
        track_download_activity = self.download_activity.filter(
            content_type=ContentType.objects.get_for_model(Track),
            object_id__in=track_ids
        )
        track_download_revenue = self.get_revenue_from_activity(
            track_download_activity,
            month=month,
            revenue_per_activity=settings.ESTIMATED_REVENUE_PER_DOWNLOAD
        )
        download_revenue = album_download_revenue + track_download_revenue

        # Determine revenue generated from streams
        album_stream_activity = self.stream_activity.filter(
            content_type=ContentType.objects.get_for_model(Album),
            object_id=self.album.id
        )
        album_stream_revenue = self.get_revenue_from_activity(
            album_stream_activity,
            month=month,
            revenue_per_activity=settings.ESTIMATED_REVENUE_PER_STREAM,
            multiplier=num_tracks
        )
        track_stream_activity = self.stream_activity.filter(
            content_type=ContentType.objects.get_for_model(Track),
            object_id__in=track_ids
        )
        track_stream_revenue = self.get_revenue_from_activity(
            track_stream_activity,
            month=month,
            revenue_per_activity=settings.ESTIMATED_REVENUE_PER_STREAM
        )
        stream_revenue = album_stream_revenue + track_stream_revenue

        total_revenue = download_revenue + stream_revenue
        return {
            'month': month.strftime("%B"),
            'artist_revenue': total_revenue * (float(self.album.project.total_artist_percentage()) / 100),
            'investor_revenue': total_revenue * (float(self.album.project.total_fans_percentage()) / 100),
        }

    def get_context_data(self, **kwargs):
        context = super(AlbumDetailView, self).get_context_data(**kwargs)

        self.album = get_object_or_404(
            Album,
            slug=kwargs['album_slug'],
            project__artist__slug=kwargs['artist_slug']
        )

        # Calculate the estimated monthly revenue
        album_track_ids = Track.objects.filter(album=self.album).values_list('id', flat=True)
        album_activity = ActivityEstimate.objects.filter(
            models.Q(content_type=ContentType.objects.get_for_model(Album), object_id=self.album.id) |
            models.Q(content_type=ContentType.objects.get_for_model(Track), object_id__in=album_track_ids)
        ).annotate(month=models.functions.TruncMonth('date')).values('month').order_by('date')
        self.download_activity = album_activity.filter(activity_type=ActivityEstimate.ACTIVITY_DOWNLOAD)
        self.stream_activity = album_activity.filter(activity_type=ActivityEstimate.ACTIVITY_STREAM)
        album_activity_months = sorted(list(set(album_activity.values_list('month', flat=True))))
        estimated_revenue = [self.estimated_revenue_month(month) for month in album_activity_months]

        user = self.request.user
        user_is_investor = user.is_authenticated and Investment.objects.filter(
            campaign__project__album=self.album,
            charge__customer__user=user,
            charge__paid=True,
            charge__refunded=False
        ).exists()

        context.update({
            'album': self.album,
            'estimated_cumulative_revenue': self.generate_cumulative_revenue(estimated_revenue),
            'user_is_investor': user_is_investor,
        })
        return context
