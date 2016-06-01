"""
:Created: 31 May 2016
:Author: Lucas Connors

"""

import os

from fabric.api import env, prefix, run, sudo


env.hosts = os.environ.get('PERDIEM_REMOTE_HOSTS', '').split(',')


def deploy():
    with prefix(". /usr/local/bin/virtualenvwrapper.sh; workon perdiem"):
        run("git pull")
        run("pip install -r ../requirements.txt")
        run("python manage.py migrate")
        run("python manage.py collectstatic --no-input")
        sudo("sv restart perdiem")
