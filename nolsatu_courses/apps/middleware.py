from functools import partial
from json import JSONDecodeError

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from requests import RequestException

from nolsatu_courses.apps.utils import update_user

SESSION_USER_ID = '_auth_user_id'
JWT_AUTH_HEADER_KEY = "X-User-Token"


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


class JWTAuthCredentialsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if (not hasattr(request, "user") or request.user.is_anonymous) and JWT_AUTH_HEADER_KEY in request.headers:
            redirect_response = redirect(
                settings.LOGIN_URL + f"?next={request.build_absolute_uri()}"
            )
            redirect_response[JWT_AUTH_HEADER_KEY] = request.headers[JWT_AUTH_HEADER_KEY]
            return redirect_response


class MobileCheckMiddleware(MiddlewareMixin):
    MOBILE_APPS_UA = ("AdinusaAndroid", "AdinusaIos")

    def process_request(self, request):
        request.is_mobile = False
        request.mobile_app = None
        request.mobile_version = None

        if 'User-Agent' in request.headers:
            user_agent = request.headers['User-Agent']
            ua_splits = user_agent.split("/")

            if len(ua_splits) != 2:
                return

            app, version = ua_splits
            if app in self.MOBILE_APPS_UA:
                request.is_mobile = True
                request.mobile_app = app
                request.mobile_version = version
