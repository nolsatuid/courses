from abc import ABC, abstractmethod
from typing import Union

from django.contrib.auth.models import AnonymousUser, User


class BaseAuthProvider(ABC):

    @abstractmethod
    def get_session_user(self, request) -> Union[AnonymousUser, User]:
        """
        Get user from session
        :param request: the request object
        :return: User when user is logged in otherwise AnonymousUser
        """
        pass

    @abstractmethod
    def get_credentials_user(self, username, password) -> User:
        """
        Get user with credentials.
        Raise AuthException if invalid credentials
        :param username: the username
        :param password: the password
        :return: User
        """
        pass


class AuthException(Exception):
    def __init__(self, message):
        self.message = message
