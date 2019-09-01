"""
WSGI config for perdiem project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

import cbsettings
from dotenv import load_dotenv


load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "perdiem.settings")
cbsettings.configure("perdiem.settings.switcher")

application = get_wsgi_application()
