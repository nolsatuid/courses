from functools import partial
from json import JSONDecodeError

from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from requests import RequestException

from nolsatu_courses.apps.utils import update_user

SESSION_USER_ID = '_auth_user_id'


def get_user(request):
    try:
        # key to cache user data use sessionid
        cache_key = request.COOKIES.get('sessionid')
        if cache_key and SESSION_USER_ID not in request.session:
            cache.delete(cache_key)
            return AnonymousUser()

        # get data user from cache
        if cache_key:
            user_cache = cache.get(cache_key)
            if user_cache:
                return user_cache

        user = update_user(request.session.get(SESSION_USER_ID))

        # cache user data
        if cache_key:
            cache.set(cache_key, user, 10 * 60)
        return user
    except (RequestException, JSONDecodeError):
        return AnonymousUser()


class NolSatuAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not hasattr(request, "user") or request.user.is_anonymous:
            request.user = SimpleLazyObject(partial(get_user, request))
