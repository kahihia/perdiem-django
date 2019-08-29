"""
:Created: 13 May 2016
:Author: Lucas Connors

"""

from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponseRedirect

from accounts.models import UserAvatar, UserAvatarURL
from emails.messages import WelcomeEmail
from emails.models import VerifiedEmail


def require_email(strategy, details, user=None, is_new=False, *args, **kwargs):
    if not details.get('email'):
        return HttpResponseRedirect(reverse('error_email_required'))


def verify_auth_operation(strategy, details, user=None, is_new=False, *args, **kwargs):
    auth_operation = kwargs['backend'].auth_operation
    if user and auth_operation == 'register':
        return HttpResponseRedirect(reverse('error_account_exists'))
    elif not user and auth_operation == 'login':
        return HttpResponseRedirect(reverse('error_account_does_not_exist'))


def mark_email_verified(strategy, details, user=None, is_new=False, *args, **kwargs):
    if user:
        VerifiedEmail.objects.update_or_create(
            defaults={'verified': True},
            user=user,
            email=details['email']
        )


def save_avatar(strategy, details, user=None, is_new=False, *args, **kwargs):
    # Skip if we don't have the user yet
    if not user:
        return

    # Get avatar from provider, skip if no avatar
    provider = kwargs['backend'].name.replace('-login', '').replace('-register', '')
    try:
        if provider == 'google-oauth2':
            avatar = kwargs['response']['image']
            is_default_avatar = avatar['isDefault']
        elif provider == 'facebook':
            avatar = kwargs['response']['picture']['data']
            is_default_avatar = avatar['is_silhouette']
        else:
            return
    except KeyError:
        return

    # Skip if the user just has the default avatar
    if is_default_avatar:
        return

    # Get avatar URL from provider
    try:
        avatar_url = avatar['url']
    except KeyError:
        return

    # For Google, use larger image than default
    if provider == 'google-oauth2':
        avatar_url = avatar_url.replace('?sz=50', '?sz=150')

    # Save avatar URL
    user_avatar, created = UserAvatar.objects.get_or_create(user=user, provider=provider)
    user_avatar_url, _ = UserAvatarURL.objects.update_or_create(avatar=user_avatar, defaults={'url': avatar_url})

    # Update user's current avatar if none was ever set
    if created and not user.userprofile.avatar:
        user.userprofile.avatar = user_avatar
        user.userprofile.save()


def send_welcome_email(strategy, details, user=None, is_new=False, *args, **kwargs):
    if user and is_new:
        user = User.objects.get(id=user.id)
        WelcomeEmail().send(user=user)
