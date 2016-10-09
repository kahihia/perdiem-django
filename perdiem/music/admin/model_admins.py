"""
:Created: 9 October 2016
:Author: Lucas Connors

"""

from django.contrib import admin

from music.admin.forms import AlbumBioAdminForm, ActivityEstimateAdminForm
from music.models import Track, Artwork, AlbumBio, MarketplaceURL, Audio


class TrackInline(admin.StackedInline):

    model = Track
    extra = 1


class ArtworkInline(admin.TabularInline):

    model = Artwork


class AlbumBioInline(admin.StackedInline):

    model = AlbumBio
    form = AlbumBioAdminForm


class MarketplaceURLInline(admin.TabularInline):

    model = MarketplaceURL


class AudioInline(admin.TabularInline):

    model = Audio


class AlbumAdmin(admin.ModelAdmin):

    raw_id_fields = ('project',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = (TrackInline, ArtworkInline, AlbumBioInline, MarketplaceURLInline, AudioInline,)


class ActivityEstimateAdmin(admin.ModelAdmin):

    form = ActivityEstimateAdminForm
