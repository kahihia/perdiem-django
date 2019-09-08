"""
:Created: 31 May 2016
:Author: Lucas Connors

"""

import os

import requests
from fabric.api import env, run, sudo
from fabric.context_managers import cd

PROJECT_DIR = "~/perdiem-django"

env.hosts = os.environ.get("PERDIEM_REMOTE_HOSTS", "").split(",")


def _pull_latest_changes():
    """
    Pull latest code from origin
    :return: Description of the changes since the last deploy
    """
    with cd(PROJECT_DIR):
        previous_commit_hash = run("git rev-parse HEAD", pty=False)
        run("git pull")
        cmd_changes_pulled = f'git log {previous_commit_hash}.. --reverse --format="%h : %an : %s" --no-color'
        changes_pulled = run(cmd_changes_pulled, pty=False)
    return changes_pulled


def _perform_update():
    """
    Update dependencies, run migrations, etc.
    """
    with cd(PROJECT_DIR):
        run("poetry install --no-dev")
        run("poetry run python manage.py migrate")
        run("poetry run python manage.py collectstatic --no-input")


def _send_notification(commits, deploy_successful):
    """
    Post update to Slack
    """
    bot_token = os.environ.get("PERDIEM_DEPLOYBOT_TOKEN")
    if not bot_token:
        return

    if commits:
        if deploy_successful:
            deploy_status = "completed successfully"
        else:
            deploy_status = "started, but was not completed successfully"
        text = f"Deploy {deploy_status}. Changelog:\n```\n{commits}\n```"
    elif deploy_successful:
        text = "Services were restarted successfully."
    else:
        text = "Attempted to restart services, but a failure occurred."

    data = {"token": bot_token, "channel": "#general", "text": text, "as_user": True}
    requests.post("https://slack.com/api/chat.postMessage", data=data)


def restart():
    """
    Restart services
    """
    sudo("sv restart perdiem")
    sudo("service nginx restart")


def deploy():
    """
    Perform update, restart services, and send notification to Slack
    """
    changes_pulled = _pull_latest_changes()

    deploy_successful = False
    try:
        _perform_update()
        restart()
        deploy_successful = True
    finally:
        _send_notification(changes_pulled, deploy_successful)
