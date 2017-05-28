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
        # django-gfklookupwidget: https://github.com/mqsoh/django-gfklookupwidget/issues/13
        'Importing from django\.core\.urlresolvers is deprecated in favor of django\.urls\.',

        # social-core: While is_authenticated is accessible as a callable, social-core will call it that way.
        # This won't be an issue once we upgrade to Django 2.0 when is_authenticated is strictly an attribute.
        # Ref:
        # https://github.com/python-social-auth/social-core/blob/4d510872460b0df94302caa8f336b165dfe4de45/social_core/utils.py#L106
        (
            'Using user\.is_authenticated\(\) and user\.is_anonymous\(\) as a method is deprecated\. '
            'Remove the parentheses to use it as an attribute\.'
        ),

        # social-app-django: https://github.com/python-social-auth/social-app-django/issues/6
        'Usage of field\.rel has been deprecated\. Use field\.remote_field instead\.',
        'Usage of ForeignObjectRel\.to attribute has been deprecated\. Use the model attribute instead\.',
    ]
    for django20warning in django20warnings:
        warnings.filterwarnings('ignore', category=RemovedInDjango20Warning, message=django20warning)

import cbsettings


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "perdiem.settings")
    cbsettings.configure('perdiem.settings.switcher')

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
