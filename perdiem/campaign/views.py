"""
:Created: 29 May 2016
:Author: Lucas Connors

"""

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.views.generic import TemplateView

from accounts.models import UserAvatar, UserProfile
from artist.models import Artist, Photo


class LeaderboardView(TemplateView):

    template_name = 'leaderboard/leaderboard.html'

    def investor_context(self, investor):
        context = investor.profile_context()
        context.update({
            'name': investor.get_display_name(),
            'url': investor.public_profile_url(),
            'avatar_url': investor.avatar_url(),
        })
        return context

    def artist_context(self, artist):
        try:
            avatar_url = artist.photo.img.url
        except Photo.DoesNotExist:
            avatar_url = UserAvatar.default_avatar_url()
        return {
            'name': artist.name,
            'url': reverse('artist', kwargs={'slug': artist.slug,}),
            'avatar_url': avatar_url,
            'total_earned': artist.total_earned,
        }

    # TODO(lucas): Review to improve performance
    # Warning: total_earned absolutely will not scale, the view is meant to
    # be run occasionally (once a day) and then have the whole page cached
    def calculate_leaderboard(self):
        # Investor total earned
        user_profiles = UserProfile.objects.filter(invest_anonymously=False)
        investor_leaders = [self.investor_context(user_profile) for user_profile in user_profiles]
        investor_leaders = filter(lambda context: context['total_earned'] > 0, investor_leaders)
        investor_leaders = sorted(investor_leaders, key=lambda context: context['total_earned'], reverse=True)[:5]

        # Artist total earned
        artists = Artist.objects.all().annotate(total_earned=models.Sum('campaign__revenuereport__amount')).filter(total_earned__isnull=False).order_by('-total_earned')[:5]
        artist_leaders = [self.artist_context(artist) for artist in artists]
        return {
            'investor_leaders': investor_leaders,
            'artist_leaders': artist_leaders,
        }

    def get_context_data(self, **kwargs):
        context = super(LeaderboardView, self).get_context_data(**kwargs)
        leaderboard = cache.get_or_set('leaderboard', self.calculate_leaderboard)
        context.update(leaderboard)
        return context
