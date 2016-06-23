"""
:Created: 12 March 2016
:Author: Lucas Connors

"""

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.html import escape

from markdown_deux.templatetags.markdown_deux_tags import markdown_allowed

from artist.managers import ArtistQuerySet
from campaign.models import Campaign


class Genre(models.Model):

    name = models.CharField(max_length=40, db_index=True, unique=True)

    def __unicode__(self):
        return self.name


class Artist(models.Model):

    name = models.CharField(max_length=60, db_index=True)
    genres = models.ManyToManyField(Genre)
    slug = models.SlugField(max_length=40, unique=True, help_text='A short label for an artist (used in URLs)')
    lat = models.DecimalField(max_digits=6, decimal_places=4, db_index=True, help_text='Latitude of artist location')
    lon = models.DecimalField(max_digits=7, decimal_places=4, db_index=True, help_text='Longitude of artist location')
    location = models.CharField(max_length=40, help_text='Description of artist location (usually city, state, country format)')

    objects = ArtistQuerySet.as_manager()

    def __unicode__(self):
        return self.name

    def latest_campaign(self):
        campaigns = Campaign.objects.filter(project__artist=self).order_by('-start_datetime')
        if campaigns:
            return campaigns[0]

    def active_campaign(self):
        active_campaigns = Campaign.objects.filter(
            project__artist=self,
            start_datetime__lt=timezone.now(),
            end_datetime__gte=timezone.now()
        ).order_by('-start_datetime')
        if active_campaigns:
            return active_campaigns[0]

    def past_campaigns(self):
        return Campaign.objects.filter(
            project__artist=self,
            end_datetime__lt=timezone.now()
        ).order_by('-end_datetime')

    def has_permission_to_submit_update(self, user):
        return user.is_authenticated() and (user.is_superuser or self.artistadmin_set.filter(user=user).exists())


class ArtistAdmin(models.Model):

    ROLE_MUSICIAN = 'musician'
    ROLE_MANAGER = 'manager'
    ROLE_PRODUCER = 'producer'
    ROLE_SONGWRITER = 'songwriter'
    ROLE_CHOICES = (
        (ROLE_MUSICIAN, 'Musician',),
        (ROLE_MANAGER, 'Manager',),
        (ROLE_PRODUCER, 'Producer',),
        (ROLE_SONGWRITER, 'Songwriter'),
    )

    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(choices=ROLE_CHOICES, max_length=12, help_text='The relationship of this user to the artist')

    def __unicode__(self):
        return unicode(self.user)


class Bio(models.Model):

    artist = models.OneToOneField(Artist, on_delete=models.CASCADE)
    bio = models.TextField(help_text='Short biography of artist. ' + markdown_allowed())

    def __unicode__(self):
        return unicode(self.artist)


class Photo(models.Model):

    artist = models.OneToOneField(Artist, on_delete=models.CASCADE)
    img = models.ImageField(upload_to='artist', help_text='Primary profile photo of artist')

    def __unicode__(self):
        return unicode(self.artist)


class SoundCloudPlaylist(models.Model):

    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    playlist = models.URLField(unique=True, help_text='The SoundCloud iframe URL to the artist\'s playlist')

    def __unicode__(self):
        return self.playlist


class Social(models.Model):

    SOCIAL_CHOICES = (
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
        ('soundcloud', 'SoundCloud'),
    )

    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    medium = models.CharField(choices=SOCIAL_CHOICES, max_length=10, help_text='The type of social network')
    url = models.URLField(unique=True, help_text='The URL to the artist\'s social network page')

    class Meta:
        unique_together = (('artist', 'medium',),)

    def __unicode__(self):
        return u'{artist}: {medium}'.format(
            artist=unicode(self.artist),
            medium=self.get_medium_display()
        )


class Update(models.Model):

    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    created_datetime = models.DateTimeField(db_index=True, auto_now_add=True)
    title = models.CharField(max_length=75)
    text = models.TextField(help_text='The content of the update')

    def __unicode__(self):
        return self.title


class UpdateImage(models.Model):

    update = models.ForeignKey(Update, on_delete=models.CASCADE)
    img = models.ImageField(upload_to='/'.join(['artist', 'updates',]))

    def __unicode__(self):
        return unicode(self.update)


class UpdateMediaURL(models.Model):

    MEDIA_IMAGE = 'image'
    MEDIA_YOUTUBE = 'youtube'
    MEDIA_CHOICES = (
        (MEDIA_IMAGE, 'Image',),
        (MEDIA_YOUTUBE, 'YouTube',),
    )

    update = models.ForeignKey(Update, on_delete=models.CASCADE)
    media_type = models.CharField(choices=MEDIA_CHOICES, max_length=8)
    url = models.URLField()

    def __unicode__(self):
        return unicode(self.update)

    def html(self):
        if self.media_type == self.MEDIA_IMAGE:
            return u"<img src=\"{url}\" alt=\"{update}\" />".format(
                url=escape(self.url),
                update=unicode(self.update)
            )
        elif self.media_type == self.MEDIA_YOUTUBE:
            url = escape(self.url)

            # A hack to correct youtu.be links and normal watch links into embed links
            # TODO: Make more robust using regex and getting all query parameters
            if 'youtu.be/' in url:
                url = url.replace('youtu.be/', 'youtube.com/watch?v=')
            url = url.replace('/watch?v=', '/embed/')

            return u"<iframe width=\"560\" height=\"315\" src=\"{url}\" frameborder=\"0\" allowfullscreen></iframe>".format(url=url)
