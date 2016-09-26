"""
:Created: 24 July 2016
:Author: Lucas Connors

"""

from django import forms
from django.contrib import admin

from pagedown.widgets import AdminPagedownWidget

from music.models import Album, Track, Artwork, AlbumBio, MarketplaceURL, Audio, ActivityEstimate


class ActivityEstimateAdminForm(forms.ModelForm):

    class Meta:
        model = ActivityEstimate
        fields = ('date', 'activity_type', 'content_type', 'object_id', 'total',)

    def clean(self):
        cleaned_data = super(ActivityEstimateAdminForm, self).clean()

        # Get the object associated with this ActivityEstimate
        content_type = cleaned_data['content_type']
        object_id = cleaned_data['object_id']
        obj = content_type.get_object_for_this_type(id=object_id)

        # Get the album associated with this ActivityEstimate
        if hasattr(obj, 'album'):
            album = obj.album
        else:
            album = obj

        # Verify that the associated album has a campaign defined
        if not album.project.campaign_set.all().exists():
            raise forms.ValidationError(
                "You cannot create activity estimates without defining the revenue percentages "
                "issued to artists and fans. You must first create a campaign."
            )

        return cleaned_data


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


class ActivityEstimateAdmin(admin.ModelAdmin):

    form = ActivityEstimateAdminForm


admin.site.register(Album, AlbumAdmin)
admin.site.register(Track)
admin.site.register(ActivityEstimate, ActivityEstimateAdmin)
