"""
:Created: 27 August 2017
:Author: Lucas Connors

"""

from django.conf import settings


def artist_settings(request):
    return {"PERDIEM_FEE": settings.PERDIEM_FEE}
