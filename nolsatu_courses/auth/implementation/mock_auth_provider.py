from typing import Union

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User

from nolsatu_courses.apps.accounts.models import MemberNolsatu
from nolsatu_courses.auth import BaseAuthProvider, AcademyAuthProvider

# Add your new mock user here
from nolsatu_courses.auth.base.auth_provider import AuthException

MOCK_USERS = {
    "admin1": {
        "user": User(
            username="admin1",
            is_staff=True,
            is_superuser=True,
            is_active=True
        ),
        "academy": MemberNolsatu(
            role=MemberNolsatu.ROLE.company,
            id_nolsatu=1,
            phone_number="08123456789"
        )
    }
}


class MockAuthProvider(BaseAuthProvider):
    @staticmethod
    def get_mock_user(username=None) -> Union[AnonymousUser, User]:
        if username:
            mock_data = MOCK_USERS.get(username, None)
            user = User.objects.filter(username=username).first()
            if not user and mock_data:
                mock_user = mock_data["user"]
                mock_user.save()

                mock_academy = mock_data["academy"]
                mock_academy.user = mock_user
                mock_academy.save()

                return mock_user

            if user:
                return user

            return AnonymousUser()

        return AnonymousUser()

    def get_session_user(self, request) -> Union[AnonymousUser, User]:
        return self.get_mock_user(getattr(settings, "MOCK_USER", None))

    def get_credentials_user(self, username, password) -> User:
        user = self.get_mock_user(username)
        if isinstance(user, AnonymousUser):
            raise AuthException("invalid user")

        return user
