"""
:Created: 26 July 2015
:Author: Lucas Connors

"""

import os

from cbsettings import DjangoDefaults
import raven
import requests


class BaseSettings(DjangoDefaults):

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    TOP_DIR = os.path.dirname(BASE_DIR)

    DEBUG = True

    @property
    def ALLOWED_HOSTS(self):
        # Get cached ALLOWED_HOSTS setting, if available
        if hasattr(self, '_ALLOWED_HOSTS'):
            return self._ALLOWED_HOSTS

        # When DEBUG == True, ALLOWED_HOSTS is just []
        if not hasattr(self, 'ACCEPTABLE_HOSTS'):
            self._ALLOWED_HOSTS = []
            return []

        # Otherwise, add EC2 IP to ACCEPTABLE_HOSTS
        hosts = self.ACCEPTABLE_HOSTS
        try:
            ec2_ip = requests.get('http://169.254.169.254/latest/meta-data/local-ipv4', timeout=0.01).text
        except requests.exceptions.RequestException:
            pass
        else:
            hosts.append(ec2_ip)
            self._ALLOWED_HOSTS = hosts
        return hosts

    # Application definition
    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'whitenoise.runserver_nostatic',
        'django.contrib.staticfiles',
        'django.contrib.sites',
        'django.contrib.humanize',
        'raven.contrib.django.raven_compat',
        'sorl.thumbnail',
        'storages',
        'rest_framework',
        'social.apps.django_app.default',
        'pinax.stripe',
        'markdown_deux',
        'pagedown',
        'accounts.apps.AccountsConfig',
        'api.apps.ApiConfig',
        'artist.apps.ArtistConfig',
        'campaign.apps.CampaignConfig',
        'emails.apps.EmailsConfig',
        'music.apps.MusicConfig',
    )
    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
        'social.apps.django_app.middleware.SocialAuthExceptionMiddleware',
        'accounts.middleware.LoginFormMiddleware',
    )
    ROOT_URLCONF = 'perdiem.urls'
    SITE_ID = 1

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(TOP_DIR, 'templates')],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                    'social.apps.django_app.context_processors.backends',
                    'social.apps.django_app.context_processors.login_redirect',
                    'perdiem.context_processors.request',
                    'accounts.context_processors.keys',
                ],
            },
        },
    ]
    WSGI_APPLICATION = 'perdiem.wsgi.application'

    # Cache and Database
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:11211',
        }
    }
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'perdiem',
            'USER': 'postgres',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '',
        }
    }

    # Internationalization
    TIME_ZONE = 'UTC'
    USE_L10N = True
    USE_TZ = True

    # Static files (CSS, JavaScript, Images)
    MEDIA_ROOT = os.path.join(TOP_DIR, 'media')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    STATIC_ROOT = os.path.join(TOP_DIR, 'staticfiles')
    STATICFILES_DIRS = (
        os.path.join(TOP_DIR, 'static'),
    )
    MEDIAFILES_LOCATION = 'media'
    STATICFILES_LOCATION = 'static'
    AWS_HEADERS = {
        'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
        'Cache-Control': 'max-age=94608000',
    }
    AWS_QUERYSTRING_AUTH = False
    MAXIMUM_AVATAR_SIZE = 2 * 1024 * 1024  # 2MB

    @property
    def MEDIA_URL(self):
        if not hasattr(self, 'AWS_S3_CUSTOM_URL'):
            return '/media/'
        return '{aws_s3}/{media}/'.format(
            aws_s3=self.AWS_S3_CUSTOM_URL,
            media=self.MEDIAFILES_LOCATION
        )

    @property
    def STATIC_URL(self):
        if not hasattr(self, 'AWS_S3_CUSTOM_URL'):
            return '/static/'
        return '{aws_s3}/{static}/'.format(
            aws_s3=self.AWS_S3_CUSTOM_URL,
            static=self.STATICFILES_LOCATION
        )

    # Authentication
    AUTHENTICATION_BACKENDS = (
        'accounts.backends.GoogleOAuth2Login',
        'accounts.backends.GoogleOAuth2Register',
        'accounts.backends.FacebookOAuth2Login',
        'accounts.backends.FacebookOAuth2Register',
        'django.contrib.auth.backends.ModelBackend',
    )
    SOCIAL_AUTH_PIPELINE = (
        'social.pipeline.social_auth.social_details',
        'social.pipeline.social_auth.social_uid',
        'social.pipeline.social_auth.auth_allowed',
        'social.pipeline.social_auth.social_user',
        'social.pipeline.user.get_username',
        'social.pipeline.social_auth.associate_by_email',
        'accounts.pipeline.require_email',
        'accounts.pipeline.verify_auth_operation',
        'social.pipeline.user.create_user',
        'accounts.pipeline.mark_email_verified',
        'accounts.pipeline.save_avatar',
        'social.pipeline.social_auth.associate_user',
        'social.pipeline.social_auth.load_extra_data',
        'social.pipeline.user.user_details',
        'accounts.pipeline.send_welcome_email',
    )
    SOCIAL_AUTH_LOGIN_ERROR_URL = '/'
    SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
    SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
        'fields': ', '.join(['id', 'name', 'email', 'picture.width(150)']),
    }
    LOGIN_URL = '/'
    LOGIN_REDIRECT_URL = '/profile/'

    @property
    def FACEBOOK_APP_ID(self):
        if not hasattr(self, 'SOCIAL_AUTH_FACEBOOK_KEY'):
            return ''
        return self.SOCIAL_AUTH_FACEBOOK_KEY

    # Sentry
    @property
    def RAVEN_CONFIG(self):
        if not hasattr(self, 'RAVEN_SECRET_KEY'):
            return {}
        return {
            'dsn': 'https://{public_key}:{secret_key}@app.getsentry.com/{project_id}'.format(
                public_key=self.RAVEN_PUBLIC_KEY,
                secret_key=self.RAVEN_SECRET_KEY,
                project_id=self.RAVEN_PROJECT_ID
            ),
            'release': raven.fetch_git_sha(self.TOP_DIR),
        }

    # Email
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = '/tmp/perdiem/email'
    TEMPLATED_EMAIL_TEMPLATE_DIR = 'email/'
    DEFAULT_FROM_EMAIL = 'PerDiem <noreply@investperdiem.com>'

    # Stripe
    PERDIEM_FEE = 1  # $1
    STRIPE_PERCENTAGE = 0.029  # 2.9%
    STRIPE_FLAT_FEE = 0.3  # $0.30
    DEFAULT_MIN_PURCHASE = 10  # $10
    PINAX_STRIPE_SEND_EMAIL_RECEIPTS = False

    # Analytics
    GA_TRACKING_CODE = ''  # Defined in prod.py
    JACO_API_KEY = ''  # Defined in prod.py
