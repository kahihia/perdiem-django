import os

import raven

from perdiem.settings.base import BaseSettings


class ProdSettings(BaseSettings):

    DEBUG = False

    # Sentry
    def RAVEN_CONFIG(self):
        return {
            'dsn': 'https://{public_key}:{secret_key}@app.getsentry.com/{project_id}'.format(
                public_key=os.environ["PERDIEM_SENTRY_PUBLIC_KEY"],
                secret_key=os.environ["PERDIEM_SENTRY_SECRET_KEY"],
                project_id=os.environ["PERDIEM_SENTRY_PROJECT_ID"]
            ),
            'release': raven.fetch_git_sha(self.TOP_DIR),
        }

    # Static files (CSS, JavaScript, Images)
    DEFAULT_FILE_STORAGE = 'django_s3_storage.storage.S3Storage'
    STATICFILES_STORAGE = 'django_s3_storage.storage.StaticS3Storage'

    def AWS_S3_BUCKET_NAME(self):
        return os.environ["PERDIEM_AWS_S3_BUCKET_NAME"]

    def AWS_S3_BUCKET_NAME_STATIC(self):
        return self.AWS_S3_BUCKET_NAME

    def AWS_ACCESS_KEY_ID(self):
        return os.environ["PERDIEM_AWS_ACCESS_KEY_ID"]

    def AWS_SECRET_ACCESS_KEY(self):
        return os.environ["PERDIEM_AWS_SECRET_ACCESS_KEY"]

    # Email
    EMAIL_BACKEND = 'django_ses.SESBackend'

    def AWS_SES_ACCESS_KEY_ID(self):
        return os.environ["PERDIEM_AWS_SES_ACCESS_KEY_ID"]

    def AWS_SES_SECRET_ACCESS_KEY(self):
        return os.environ["PERDIEM_AWS_SES_SECRET_ACCESS_KEY"]
