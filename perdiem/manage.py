#!/usr/bin/env python
import os
import sys
import warnings

from django.utils.deprecation import RemovedInDjango20Warning

# Propagate warnings as errors when running tests
if len(sys.argv) >= 2 and sys.argv[1] == 'test':
    warnings.filterwarnings('error')
    # Filter warnings that are a result of dependencies
    # They can be removed once the dependency fixes the issue
    django20warnings = [
        'on_delete will be a required arg for .*', # pinax-stripe: https://github.com/pinax/pinax-stripe/issues/255
        'Old-style middleware using settings\.MIDDLEWARE_CLASSES is deprecated\. Update your middleware and use settings.MIDDLEWARE instead\.', # python-social-auth: https://github.com/omab/python-social-auth/issues/953
        'Importing from django\.core\.urlresolvers is deprecated in favor of django\.urls\.', # python-social-auth: https://github.com/omab/python-social-auth/issues/979
    ]
    for django20warning in django20warnings:
        warnings.filterwarnings('ignore', category=RemovedInDjango20Warning, message=django20warning)

import cbsettings


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "perdiem.settings")
    cbsettings.configure('perdiem.settings.switcher')

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
