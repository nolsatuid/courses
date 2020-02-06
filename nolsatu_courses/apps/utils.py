import datetime

import requests
from django.conf import settings
from django.utils.text import slugify


def generate_unique_slug(klass, field, id):
    """
    generate unique slug.
    """
    origin_slug = slugify(field)
    unique_slug = origin_slug
    numb = 1
    obj = klass.objects.filter(slug=unique_slug).first()
    while obj:
        if obj.id == id:
            break
        unique_slug = '%s-%d' % (origin_slug, numb)
        numb += 1
        obj = klass.objects.filter(slug=unique_slug).first()
    return unique_slug


def post_inbox(request, user, subject, content):
    notif_endpoint = f'{settings.NOLSATU_HOST}/api/notifications/inbox'

    data = {
        'user': user.nolsatu.id_nolsatu,
        'subject': subject,
        'content': content,
        'session_key': request.COOKIES.get('sessionid')
    }

    requests.post(notif_endpoint, data=data)


def call_internal_api(method, url, **kwargs):
    method_map = {
        'get': requests.get,
        'post': requests.post,
        'put': requests.put,
        'patch': requests.patch,
        'delete': requests.delete
    }
    headers = {
        "authorization": {
            'server_key': settings.SERVER_KEY,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
        }
    }

    return method_map[method](url, headers=headers, **kwargs)
