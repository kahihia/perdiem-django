import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from perdiem.settings.base import BaseSettings


class ProdSettings(BaseSettings):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        sentry_sdk.init(
            dsn=os.environ["PERDIEM_SENTRY_DSN"], integrations=[DjangoIntegration()]
        )

    DEBUG = False

    # Static files (CSS, JavaScript, Images)
    DEFAULT_FILE_STORAGE = "django_s3_storage.storage.S3Storage"
    STATICFILES_STORAGE = "django_s3_storage.storage.StaticS3Storage"

    @property
    def AWS_S3_BUCKET_NAME(self):
        return os.environ["PERDIEM_AWS_S3_BUCKET_NAME"]

    @property
    def AWS_S3_BUCKET_NAME_STATIC(self):
        return self.AWS_S3_BUCKET_NAME

    @property
    def AWS_ACCESS_KEY_ID(self):
        return os.environ["PERDIEM_AWS_ACCESS_KEY_ID"]

    @property
    def AWS_SECRET_ACCESS_KEY(self):
        return os.environ["PERDIEM_AWS_SECRET_ACCESS_KEY"]

    # Email
    EMAIL_BACKEND = "django_ses.SESBackend"

    @property
    def AWS_SES_ACCESS_KEY_ID(self):
        return os.environ["PERDIEM_AWS_SES_ACCESS_KEY_ID"]

    @property
    def AWS_SES_SECRET_ACCESS_KEY(self):
        return os.environ["PERDIEM_AWS_SES_SECRET_ACCESS_KEY"]
