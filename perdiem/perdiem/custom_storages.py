"""
:Created: 15 May 2016
:Author: Lucas Connors

"""

from django.conf import settings
from django.contrib.staticfiles.storage import ManifestFilesMixin

from storages.backends.s3boto import S3BotoStorage


class StaticStorage(ManifestFilesMixin, S3BotoStorage):
    location = settings.STATICFILES_LOCATION


class MediaStorage(S3BotoStorage):
    location = settings.MEDIAFILES_LOCATION
