"""
:Created: 29 May 2016
:Author: Lucas Connors

"""

from django.core.cache import cache
from django.db import models
from django.views.generic import TemplateView

from accounts.models import UserProfile


class LeaderboardView(TemplateView):

    template_name = 'leaderboard/leaderboard.html'

    # TODO(lucas): Review to improve performance
    # Warning: This absolutely will not scale, the view is meant to be run
    # occasionally (once a day) and then have the whole page cached
    def calculate_leaderboard(self):
        all_users = [(userp, userp.profile_context()) for userp in UserProfile.objects.filter(invest_anonymously=False)]
        highest_roi = filter(lambda (userp, pcontext): pcontext['total_earned'] > 0, all_users)
        highest_roi = sorted(highest_roi, key=lambda (userp, pcontext): pcontext['total_earned'], reverse=True)[:5]
        return {
            'highest_roi': highest_roi,
        }

    def get_context_data(self, **kwargs):
        context = super(LeaderboardView, self).get_context_data(**kwargs)
        leaderboard = cache.get_or_set('leaderboard', self.calculate_leaderboard)
        context.update(leaderboard)
        return context
