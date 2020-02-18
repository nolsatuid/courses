from json import JSONDecodeError

import jwt
from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.utils.translation import ugettext_lazy as _
from jwt import InvalidTokenError
from requests import RequestException
from rest_framework import HTTP_HEADER_ENCODING
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken

from nolsatu_courses.apps.utils import update_user


class InternalAPIAuthentication(BaseAuthentication):
    def authenticate(self, request):
        self.validate_token(request)
        return AnonymousUser(), None

    def validate_token(self, request):
        header = self.get_header(request)
        if header is None:
            return None
        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        if validated_token.get("server_key", None) != settings.SERVER_KEY:
            raise InvalidToken(_('Token contained no recognizable server key'))

        return validated_token

    def get_header(self, request):
        """
        Extracts the header containing the JSON web token from the given
        request.
        """
        header = request.META.get('HTTP_AUTHORIZATION')
        #
        if isinstance(header, str):
            # Work around django test client oddness
            header = header.encode(HTTP_HEADER_ENCODING)

        return header

    def get_raw_token(self, header):
        """
        Extracts an unvalidated JSON web token from the given "Authorization"
        header value.
        """
        parts = header.split()

        if len(parts) == 0:
            # Empty AUTHORIZATION header sent
            return None

        if parts[0].decode(HTTP_HEADER_ENCODING) != "Server":
            # Assume the header does not contain a JSON web token
            raise AuthenticationFailed(
                _('Authorization not from server'),
                code='bad_authorization_header',
            )

        if len(parts) != 2:
            raise AuthenticationFailed(
                _('Authorization header must contain two space-delimited values'),
                code='bad_authorization_header',
            )

        return parts[1]

    def get_validated_token(self, raw_token):
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        messages = []
        try:
            raw_token = raw_token.decode(HTTP_HEADER_ENCODING)
            return jwt.decode(raw_token, settings.SECRET_KEY)
        except InvalidTokenError as e:
            messages.append(str(e))

        raise InvalidToken({
            'detail': _('Given token not valid for any token type'),
            'messages': messages,
        })


class UserAPIServiceAuthentication(InternalAPIAuthentication):
    def authenticate(self, request):
        validated_token = self.validate_token(request)
        return self.get_user(validated_token), None

    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token["user_id"]
        except KeyError:
            raise InvalidToken(_('Token contained no recognizable user identification'))

        user = User.objects.filter(nolsatu__id_nolsatu=user_id).first()
        if not user:
            try:
                return update_user(user_id)
            except (RequestException, JSONDecodeError):
                return AnonymousUser()

        return user


class UserAuthAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (UserAPIServiceAuthentication,)