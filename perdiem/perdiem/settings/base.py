"""
:Created: 26 July 2015
:Author: Lucas Connors

"""

import os

from cbsettings import DjangoDefaults


class BaseSettings(DjangoDefaults):

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    TOP_DIR = os.path.dirname(BASE_DIR)

    DEBUG = True
    ALLOWED_HOSTS = []

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
        'pinax.stripe',
        'accounts.apps.AccountsConfig',
        'artist.apps.ArtistConfig',
        'campaign.apps.CampaignConfig',
        'emails.apps.EmailsConfig',
    )
    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
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
                ],
            },
        },
    ]
    WSGI_APPLICATION = 'perdiem.wsgi.application'

    # Database
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
    MEDIA_URL = '/media/'
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    STATIC_ROOT = os.path.join(TOP_DIR, 'staticfiles')
    STATICFILES_DIRS = (
        os.path.join(TOP_DIR, 'static'),
    )
    STATIC_URL = '/static/'

    # Email
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = '/tmp/perdiem/email'
    TEMPLATED_EMAIL_TEMPLATE_DIR = 'email/'
    DEFAULT_FROM_EMAIL = 'noreply@investperdiem.com'

    # Stripe
    PERDIEM_FEE = 1 # $1
    PINAX_STRIPE_SEND_EMAIL_RECEIPTS = False
