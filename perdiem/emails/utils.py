"""
:Created: 17 April 2016
:Author: Lucas Connors

"""

from django.contrib.sites.models import Site
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.core.urlresolvers import reverse


def make_token(user):
    return TimestampSigner().sign(user.username)

def create_unsubscribe_link(user):
    username, token = make_token(user).split(":", 1)
    unsubscribe_url = reverse('unsubscribe', kwargs={'username': username, 'token': token,})
    return "http://{domain}{url}".format(
        domain=Site.objects.get_current().domain,
        url=unsubscribe_url
    )

def check_token(username, token):
    try:
        key = '%s:%s' % (username, token)
        TimestampSigner().unsign(key, max_age=60 * 60 * 48) # Valid for 2 days
    except (BadSignature, SignatureExpired):
        return False
    return True
