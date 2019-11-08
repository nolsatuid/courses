from functools import partial
from json import JSONDecodeError

import requests
from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from requests import RequestException


def get_user(request):
    try:
        # Make it more faster? cache?
        data = requests.get(settings.NOLSATU_PROFILE_URL, cookies=request.COOKIES).json()
        return User(
            id=data['id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            username=data['username'],
            email=data['email'],
            is_active=data['is_active'],
            is_staff=data['is_staff'],
            is_superuser=data['is_superuser']
        )
    except (RequestException, JSONDecodeError):
        return AnonymousUser()


class NolSatuAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not hasattr(request, "user") or request.user.is_anonymous:
            request.user = SimpleLazyObject(partial(get_user, request))
