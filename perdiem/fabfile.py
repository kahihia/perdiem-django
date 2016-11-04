"""
:Created: 31 May 2016
:Author: Lucas Connors

"""

import os

from fabric.api import env, prefix, run, sudo
import requests


env.hosts = os.environ.get('PERDIEM_REMOTE_HOSTS', '').split(',')


def send_notification(commit):
    bot_token = os.environ.get('PERDIEM_DEPLOYBOT_TOKEN')
    if not bot_token:
        return

    data = {
        'token': bot_token,
        'channel': '#general',
        'text': '`{commit}`\nhas been deployed'.format(commit=commit),
        'as_user': True,
    }
    requests.post('https://slack.com/api/chat.postMessage', data=data)


def deploy():
    with prefix(". /usr/local/bin/virtualenvwrapper.sh; workon perdiem"):
        run("git pull")
        latest_commit = run("git log -1 --format=\"%h : %an : %s\" --no-color", pty=False)
        run("pip install -r ../requirements.txt")
        run("python manage.py migrate")
        run("python manage.py collectstatic --no-input")
        sudo("sv restart perdiem")
    send_notification(latest_commit)
