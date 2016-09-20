"""
:Created: 24 July 2016
:Author: Lucas Connors

"""

from django import forms
from django.contrib import admin

from pagedown.widgets import AdminPagedownWidget

from music.models import Album, Track, Artwork, AlbumBio, MarketplaceURL, Audio, ActivityEstimate


class TrackInline(admin.StackedInline):

    model = Track
    extra = 1


class ArtworkInline(admin.TabularInline):

    model = Artwork


class AlbumBioAdminForm(forms.ModelForm):

    bio = forms.CharField(help_text=AlbumBio._meta.get_field('bio').help_text, widget=AdminPagedownWidget)

    class Meta:
        model = AlbumBio
        fields = ('bio',)


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


admin.site.register(Album, AlbumAdmin)
admin.site.register(Track)
admin.site.register(ActivityEstimate)
