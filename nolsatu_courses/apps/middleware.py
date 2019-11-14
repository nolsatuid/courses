from functools import partial
from json import JSONDecodeError

import requests
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import User, AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from requests import RequestException

LOGIN_CHECK_KEY = '_auth_user_id'


def get_user(request):
    try:
        # key to cache user data use csrftoken
        cache_key = request.COOKIES['csrftoken']
        if LOGIN_CHECK_KEY not in request.session:
            cache.delete(cache_key)
            return AnonymousUser()

        # get data user from cache
        user_cache = cache.get(cache_key)
        if user_cache:
            return user_cache

        # get authentication from Nolsatu
        data = requests.get(settings.NOLSATU_PROFILE_URL, cookies=request.COOKIES).json()
        defaults = {
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'is_active': data['is_active'],
            'is_staff': data['is_staff'],
            'is_superuser': data['is_superuser']
        }
        # get or create user
        user, created = User.objects.get_or_create(
            username=data['username'],
            email=data['email'],
            defaults={**defaults},
        )

        if created:
            # save other data from nolsatu to model UserNolsatu
            pass

        # cache user data
        cache.set(cache_key, user)
        return user
    except (RequestException, JSONDecodeError):
        return AnonymousUser()


class NolSatuAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not hasattr(request, "user") or request.user.is_anonymous:
            request.user = SimpleLazyObject(partial(get_user, request))
