from django.conf import settings
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

from nolsatu_courses.auth import auth_provider

JWT_AUTH_HEADER_KEY = "X-User-Token"


class SharedSessionAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.user = SimpleLazyObject(lambda: auth_provider.get_session_user(request))


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
