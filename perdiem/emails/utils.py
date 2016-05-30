"""
:Created: 17 April 2016
:Author: Lucas Connors

"""

from django.contrib.sites.models import Site
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.core.urlresolvers import reverse

from emails.models import EmailSubscription


def make_token(user):
    return TimestampSigner().sign(user.id)

def create_unsubscribe_link(user, subscription_type=EmailSubscription.SUBSCRIPTION_ALL):
    user_id, token = make_token(user).split(":", 1)
    unsubscribe_url = reverse(
        'unsubscribe',
        kwargs={
            'user_id': user_id,
            'subscription_type': subscription_type,
            'token': token,
        }
    )
    return "http://{domain}{url}".format(
        domain=Site.objects.get_current().domain,
        url=unsubscribe_url
    )

def check_token(user_id, token):
    try:
        key = '%s:%s' % (user_id, token)
        TimestampSigner().unsign(key, max_age=60 * 60 * 48) # Valid for 2 days
    except (BadSignature, SignatureExpired):
        return False
    return True
