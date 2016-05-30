"""
:Created: 29 May 2016
:Author: Lucas Connors

"""

from django.core.cache import cache
from django.db import models
from django.dispatch import receiver

from campaign.models import RevenueReport


@receiver(models.signals.post_save, sender=RevenueReport, dispatch_uid="clear_leaderboard_cache_handler")
def clear_leaderboard_cache_handler(sender, instance, **kwargs):
    cache.delete('leaderboard')
