import requests
from django.conf import settings
from django.utils.text import slugify


def generate_unique_slug(klass, field):
    """
    return unique slug if origin slug is exist.
    eg: `foo-bar` => `foo-bar-1`

    :param `klass` is Class model.
    :param `field` is specific field for title.
    """
    origin_slug = slugify(field)
    unique_slug = origin_slug
    numb = 1
    while klass.objects.filter(slug=unique_slug).exists():
        unique_slug = '%s-%d' % (origin_slug, numb)
        numb += 1
    return unique_slug


def post_inbox(user, subject, content):
    notif_endpoint = f'{settings.NOLSATU_HOST}/api/notifications'

    data = {
        'user': user.nolsatu.id_nolsatu,
        'subject': subject,
        'content': content
    }

    requests.post(notif_endpoint, data)
