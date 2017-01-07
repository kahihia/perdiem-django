"""
:Created: 24 July 2016
:Author: Lucas Connors

"""

from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone

from boto.s3.connection import S3Connection
from gfklookupwidget.fields import GfkLookupField
from markdown_deux.templatetags.markdown_deux_tags import markdown_allowed

from campaign.models import Project
from render.url.utils import add_params_to_url


class Album(models.Model):

    project = models.ForeignKey(Project)
    name = models.CharField(max_length=60)
    slug = models.SlugField(max_length=40, db_index=True, help_text='A short label for an album (used in URLs)')
    release_date = models.DateField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    def validate_unique(self, exclude=None):
        if Album.objects.exclude(id=self.id).filter(project__artist=self.project.artist, slug=self.slug).exists():
            raise ValidationError("Slug must be unique per artist")

    def save(self, *args, **kwargs):
        self.validate_unique()
        super(Album, self).save(*args, **kwargs)

    def url(self):
        return reverse('album', kwargs={'artist_slug': self.project.artist.slug, 'album_slug': self.slug})

    def discs(self):
        disc_numbers = self.track_set.all().values_list('disc_number', flat=True).distinct().order_by('disc_number')
        return (self.track_set.filter(disc_number=disc).order_by('track_number') for disc in disc_numbers)


class Track(models.Model):

    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    disc_number = models.PositiveSmallIntegerField(default=1)
    track_number = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=60)
    duration = models.DurationField(null=True, blank=True)

    class Meta:
        unique_together = (('album', 'disc_number', 'track_number',),)

    def __unicode__(self):
        return "{album} #{track_number}: {name}".format(
            album=unicode(self.album),
            track_number=self.track_number,
            name=self.name
        )

    def total_activity(self, activity_type):
        return ActivityEstimate.objects.filter(
            models.Q(content_type=ContentType.objects.get_for_model(self.album), object_id=self.album.id) |
            models.Q(content_type=ContentType.objects.get_for_model(self), object_id=self.id),
            activity_type=activity_type
        ).aggregate(total=models.Sum('total'))['total'] or 0

    def total_downloads(self):
        return self.total_activity(ActivityEstimate.ACTIVITY_DOWNLOAD)

    def total_streams(self):
        return self.total_activity(ActivityEstimate.ACTIVITY_STREAM)


class Artwork(models.Model):

    album = models.OneToOneField(Album)
    img = models.ImageField(upload_to='artist/album')

    class Meta:
        verbose_name_plural = 'Artwork'

    def __unicode__(self):
        return unicode(self.album)


class AlbumBio(models.Model):

    album = models.OneToOneField(Album)
    bio = models.TextField(help_text='Tracklisting and other info about the album. ' + markdown_allowed())

    def __unicode__(self):
        return unicode(self.album)


class MarketplaceURL(models.Model):

    MARKETPLACE_ITUNES = 'itunes'
    MARKETPLACE_APPLE_MUSIC = 'apple'
    MARKETPLACE_CHOICES = (
        ('spotify', 'Spotify',),
        (MARKETPLACE_ITUNES, 'iTunes',),
        (MARKETPLACE_APPLE_MUSIC, 'Apple Music',),
        ('google', 'Google Play',),
        ('amazon', 'Amazon',),
        ('tidal', 'Tidal',),
        ('youtube', 'YouTube',),
    )

    album = models.ForeignKey(Album)
    medium = models.CharField(choices=MARKETPLACE_CHOICES, max_length=10, help_text='The type of marketplace')
    url = models.URLField(unique=True, help_text='The URL to the album\'s page')

    class Meta:
        unique_together = (('album', 'medium',),)

    def __unicode__(self):
        return u'{album}: {medium}'.format(
            album=unicode(self.album),
            medium=self.get_medium_display()
        )

    def marketplace_has_affiliate_token(self):
        return self.medium in (self.MARKETPLACE_ITUNES, self.MARKETPLACE_APPLE_MUSIC,)

    def affiliate_url(self):
        if self.marketplace_has_affiliate_token() and hasattr(settings, 'ITUNES_AFFILIATE_TOKEN'):
            return add_params_to_url(self.url, {'at': settings.ITUNES_AFFILIATE_TOKEN})
        return self.url


class S3PrivateFileField(models.FileField):

    def __init__(self, verbose_name=None, name=None, upload_to='', storage=None, **kwargs):
        super(S3PrivateFileField, self).__init__(
            verbose_name=verbose_name,
            name=name,
            upload_to=upload_to,
            storage=storage,
            **kwargs
        )
        self.storage.default_acl = "private"


class Audio(models.Model):

    album = models.OneToOneField(Album)
    file = S3PrivateFileField(upload_to='artist/audio')

    class Meta:
        verbose_name_plural = 'Audio'

    def __unicode__(self):
        return unicode(self.album)

    def get_temporary_url(self, ttl=60):
        if hasattr(settings, 'AWS_STORAGE_BUCKET_NAME'):
            s3 = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, is_secure=True)
            key = "{media}/{filename}".format(media=settings.MEDIAFILES_LOCATION, filename=self.file.name)
            return s3.generate_url(ttl, 'GET', bucket=settings.AWS_STORAGE_BUCKET_NAME, key=key)
        return self.file.url


def activity_content_type_choices():
    return {
        'id__in': (
            ContentType.objects.get_for_model(Album).id,
            ContentType.objects.get_for_model(Track).id,
        )
    }


class ActivityEstimate(models.Model):

    ACTIVITY_STREAM = 'stream'
    ACTIVITY_DOWNLOAD = 'download'
    ACTIVITY_CHOICES = (
        (ACTIVITY_STREAM, 'Stream',),
        (ACTIVITY_DOWNLOAD, 'Download',),
    )

    date = models.DateField(default=timezone.now)
    activity_type = models.CharField(choices=ACTIVITY_CHOICES, max_length=8)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.PROTECT, limit_choices_to=activity_content_type_choices
    )
    object_id = GfkLookupField('content_type')
    content_object = GenericForeignKey()
    total = models.PositiveIntegerField()

    class Meta:
        unique_together = (('date', 'activity_type', 'content_type', 'object_id',),)

    def __unicode__(self):
        return unicode(self.content_object)
