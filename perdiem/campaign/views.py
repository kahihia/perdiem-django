"""
:Created: 29 May 2016
:Author: Lucas Connors

"""

from django.core.cache import cache
from django.views.generic import TemplateView

from accounts.models import UserProfile


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

    # TODO(lucas): Review to improve performance
    # Warning: top_earned_investors absolutely will not scale, the view is meant
    # to be run occasionally (once a day) and then have the whole page cached
    def calculate_leaderboard(self):
        # Top earned investors
        user_profiles = UserProfile.objects.filter(invest_anonymously=False)
        top_earned_investors = [self.investor_context(user_profile, 'total_earned') for user_profile in user_profiles]
        top_earned_investors = list(filter(lambda context: context['amount'] > 0, top_earned_investors))
        top_earned_investors = sorted(top_earned_investors, key=lambda context: context['amount'], reverse=True)[:20]

        return {
            'top_earned_investors': top_earned_investors,
        }

    def get_context_data(self, **kwargs):
        context = super(LeaderboardView, self).get_context_data(**kwargs)
        leaderboard = cache.get_or_set('leaderboard', self.calculate_leaderboard)
        context.update(leaderboard)
        return context
