from json import JSONDecodeError
from typing import Union

import requests
from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth import SESSION_KEY as AUTH_SESSION_KEY
from django.core.cache import cache
from requests import RequestException

from nolsatu_courses.apps.utils import update_user
from nolsatu_courses.auth import BaseAuthProvider
from nolsatu_courses.auth.base.auth_provider import AuthException
from django.utils.translation import ugettext_lazy as _


class AcademyAuthProvider(BaseAuthProvider):
    def get_session_user(self, request) -> Union[AnonymousUser, User]:
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

    def get_credentials_user(self, username, password) -> User:
        credentials = {
            'username': username,
            'password': password
        }

        response = requests.post(f'{settings.NOLSATU_HOST}/api/auth/login', data=credentials)
        if response.status_code == 200:
            user_id = response.json()['user']['id']

            user = User.objects.filter(nolsatu__id_nolsatu=user_id).first()
            if not user:
                try:
                    return update_user(user_id)
                except (RequestException, JSONDecodeError):
                    raise AuthException(_('Invalid username/password.'))
            return user
        else:
            raise AuthException(_('Invalid username/password.'))
