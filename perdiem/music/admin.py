"""
:Created: 24 July 2016
:Author: Lucas Connors

"""

from django.contrib import admin

from music.models import Album, Artwork, MarketplaceURL, Audio


class ArtworkInline(admin.TabularInline):

    model = Artwork


class MarketplaceURLInline(admin.TabularInline):

    model = MarketplaceURL


class AudioInline(admin.TabularInline):

    model = Audio


class AlbumAdmin(admin.ModelAdmin):

    raw_id_fields = ('project',)
    prepopulated_fields = {'slug': ('name',),}
    inlines = (ArtworkInline, MarketplaceURLInline, AudioInline,)


admin.site.register(Album, AlbumAdmin)
