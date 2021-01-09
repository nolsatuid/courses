from functools import partial
from json import JSONDecodeError

from django.conf import settings
from django.contrib.auth import SESSION_KEY as AUTH_SESSION_KEY
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from requests import RequestException

from nolsatu_courses.apps.utils import update_user

JWT_AUTH_HEADER_KEY = "X-User-Token"


def get_user(request):
    try:
        auth_session_user_id = request.session.get(AUTH_SESSION_KEY, None)
        cache_key = f"USER_CACHE_{auth_session_user_id}" if auth_session_user_id else None

        # No Auth Session
        if not auth_session_user_id:
            return AnonymousUser()

        user_cache = cache.get(cache_key)

        # Cache hit
        if user_cache:
            return user_cache

        # Get user from other service
        user = update_user(auth_session_user_id)

        # cache user data
        cache.set(cache_key, user, 10 * 60)

        return user
    except (RequestException, JSONDecodeError):
        return AnonymousUser()


class SharedSessionAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not hasattr(request, "user") or request.user.is_anonymous:
            request.user = SimpleLazyObject(partial(get_user, request))


class JWTAuthCredentialsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if (not hasattr(request, "user") or request.user.is_anonymous) and JWT_AUTH_HEADER_KEY in request.headers:
            # LOGIN_URL yang di atur harus memiliki minimal 1 query param.
            # Dikarenakan saat menambah query next disini menggunakan &
            redirect_response = redirect(
                settings.LOGIN_URL + f"&next={request.build_absolute_uri()}"
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
