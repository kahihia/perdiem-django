"""
:Created: 9 July 2016
:Author: Lucas Connors

"""

from django.conf import settings


def keys(request):
    return {
        'GA_TRACKING_CODE': settings.GA_TRACKING_CODE,
        'JACO_API_KEY': settings.JACO_API_KEY,
    }
