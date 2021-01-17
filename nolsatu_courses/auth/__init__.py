from django.conf import settings

from nolsatu_courses.auth.base.auth_provider import BaseAuthProvider
from nolsatu_courses.auth.implementation.academy_auth_provider import AcademyAuthProvider
from nolsatu_courses.auth.implementation.mock_auth_provider import MockAuthProvider


def _get_auth_provider() -> BaseAuthProvider:
    if getattr(settings, "ENABLE_MOCK_USER", False):
        return MockAuthProvider()

    return AcademyAuthProvider()


auth_provider = _get_auth_provider()
