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

    def investor_context(self, investor, key_to_copy):
        context = investor.profile_context()
        context['amount'] = context[key_to_copy]
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
            'amount': artist.amount,
        }

    # TODO(lucas): Review to improve performance
    # Warning: top_invested and top_earned_investors absolutely will not scale,
    # the view is meant to be run occasionally (once a day) and then have the
    # whole page cached
    def calculate_leaderboard(self):
        # Top raised
        all_artists = Artist.objects.all()
        top_raised = all_artists.annotate(
            amount=models.Sum(
                models.Case(
                    models.When(
                        project__campaign__investment__charge__paid=True,
                        then=models.F('project__campaign__investment__num_shares') * models.F('project__campaign__value_per_share')
                    ),
                    default=0,
                    output_field=models.IntegerField()
                )
            )
        ).filter(amount__gt=0).order_by('-amount')[:5]
        top_raised = [self.artist_context(artist) for artist in top_raised]

        # Top invested
        user_profiles = UserProfile.objects.filter(invest_anonymously=False)
        top_invested = [self.investor_context(user_profile, 'total_investments') for user_profile in user_profiles]
        top_invested = filter(lambda context: context['amount'] > 0, top_invested)
        top_invested = sorted(top_invested, key=lambda context: context['amount'], reverse=True)[:5]

        # Top earned investors
        top_earned_investors = [self.investor_context(user_profile, 'total_earned') for user_profile in user_profiles]
        top_earned_investors = filter(lambda context: context['amount'] > 0, top_earned_investors)
        top_earned_investors = sorted(top_earned_investors, key=lambda context: context['amount'], reverse=True)[:5]

        # Top earned artists
        top_earned_artists = all_artists.annotate(amount=models.Sum('project__revenuereport__amount')).filter(amount__isnull=False).order_by('-amount')[:5]
        top_earned_artists = [self.artist_context(artist) for artist in top_earned_artists]

        return {
            'top_raised': top_raised,
            'top_invested': top_invested,
            'top_earned_artists': top_earned_artists,
            'top_earned_investors': top_earned_investors,
        }

    def get_context_data(self, **kwargs):
        context = super(LeaderboardView, self).get_context_data(**kwargs)
        leaderboard = cache.get_or_set('leaderboard', self.calculate_leaderboard)
        context.update(leaderboard)
        return context
