"""
:Created: 20 September 2016
:Author: Lucas Connors

"""

import urllib
import urlparse


def add_params_to_url(url, params):
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urllib.urlencode(query)
    return urlparse.urlunparse(url_parts)
