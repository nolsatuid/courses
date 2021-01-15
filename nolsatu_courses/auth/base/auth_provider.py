from abc import ABC, abstractmethod
from typing import Union

from django.contrib.auth.models import AnonymousUser, User


class BaseAuthProvider(ABC):

    @abstractmethod
    def get_session_user(self, request) -> Union[AnonymousUser, User]:
        pass

    @abstractmethod
    def get_credentials_user(self, username, password) -> Union[AnonymousUser, User]:
        pass


class AuthException(Exception):
    def __init__(self, message):
        self.message = message
