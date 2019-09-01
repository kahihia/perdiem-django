"""
:Created: 31 May 2016
:Author: Lucas Connors

"""

import os

from fabric.api import env, prefix, run, sudo
from fabric.context_managers import cd
import requests


env.hosts = os.environ.get("PERDIEM_REMOTE_HOSTS", "").split(",")


def send_notification(commits):
    bot_token = os.environ.get("PERDIEM_DEPLOYBOT_TOKEN")
    if not bot_token:
        return

    text = (
        "```\n{commits}\n```\nhas been deployed".format(commits=commits)
        if commits
        else "Services were restarted"
    )
    data = {"token": bot_token, "channel": "#general", "text": text, "as_user": True}
    requests.post("https://slack.com/api/chat.postMessage", data=data)


def deploy():
    with cd("~/perdiem-django"):
        previous_commit_hash = run('git log -1 --format="%H" --no-color', pty=False)
        run("git pull")
        cmd_changes_deployed = 'git log {previous_hash}.. --reverse --format="%h : %an : %s" --no-color'.format(
            previous_hash=previous_commit_hash
        )
        changes_deployed = run(cmd_changes_deployed, pty=False)
        run("poetry install --no-dev")
        run("poetry run python manage.py migrate")
        run("poetry run python manage.py collectstatic --no-input")
        sudo("sv restart perdiem")
    send_notification(changes_deployed)
