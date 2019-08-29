"""
:Created: 24 July 2016
:Author: Lucas Connors

"""

from django.contrib import admin

from music.admin.model_admins import AlbumAdmin, ActivityEstimateAdmin
from music.models import Album, Track, ActivityEstimate


admin.site.register(Album, AlbumAdmin)
admin.site.register(Track)
admin.site.register(ActivityEstimate, ActivityEstimateAdmin)
