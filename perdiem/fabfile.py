"""
:Created: 31 May 2016
:Author: Lucas Connors

"""

import os

from fabric.api import env, prefix, run, sudo
import requests


env.hosts = os.environ.get('PERDIEM_REMOTE_HOSTS', '').split(',')


def send_notification(commits):
    bot_token = os.environ.get('PERDIEM_DEPLOYBOT_TOKEN')
    if not bot_token:
        return

    data = {
        'token': bot_token,
        'channel': '#general',
        'text': '```\n{commits}\n```\nhas been deployed'.format(commits=commits),
        'as_user': True,
    }
    requests.post('https://slack.com/api/chat.postMessage', data=data)


def deploy():
    with prefix(". /usr/local/bin/virtualenvwrapper.sh; workon perdiem"):
        previous_commit_hash = run("git log -1 --format=\"%H\" --no-color", pty=False)
        run("git pull")
        cmd_changes_deployed = "git log {previous_hash}.. --format=\"%h : %an : %s\" --no-color".format(
            previous_hash=previous_commit_hash
        )
        changes_deployed = run(cmd_changes_deployed, pty=False)
        run("pip install -r ../requirements.txt")
        run("python manage.py migrate")
        run("python manage.py collectstatic --no-input")
        sudo("sv restart perdiem")
    send_notification(changes_deployed)
