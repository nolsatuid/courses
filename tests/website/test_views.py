from tests import CourseTestCase
from django.urls import reverse

from django.contrib.auth.models import User


class AuthUserViewTest(CourseTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        url = reverse('website:login')
        response = self.client.get(url)

        # redirect to app academy
        self.assertEqual(response.status_code, 302)
