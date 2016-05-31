"""
:Created: 17 April 2016
:Author: Lucas Connors

"""

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

from emails.managers import EmailSubscriptionManager


class EmailSubscription(models.Model):

    SUBSCRIPTION_ALL = 'ALL'
    SUBSCRIPTION_NEWS = 'NEWS'
    SUBSCRIPTION_ARTUP = 'ARTUP'
    SUBSCRIPTION_CHOICES = (
        (SUBSCRIPTION_ALL, 'General',),
        (SUBSCRIPTION_NEWS, 'Newsletter',),
        (SUBSCRIPTION_ARTUP, 'Artist Updates',),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.CharField(choices=SUBSCRIPTION_CHOICES, max_length=6, default=SUBSCRIPTION_ALL)
    subscribed = models.BooleanField(default=True)

    objects = EmailSubscriptionManager()

    class Meta:
        unique_together = (('user', 'subscription',),)

    def __unicode__(self):
        return unicode(self.user)
