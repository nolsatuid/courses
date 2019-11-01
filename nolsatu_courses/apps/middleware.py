import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.deprecation import MiddlewareMixin


class NolSatuAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not hasattr(request, "user") or request.user.is_anonymous:
            try:
                data = requests.get(settings.NOLSATU_PROFILE_URL, cookies=request.COOKIES).json()
                request.user = User(first_name=data['first_name']) # TODO: Mapping
            except Exception:
                pass
