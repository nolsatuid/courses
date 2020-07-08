from tests import CourseTestCase
from django.urls import reverse


class AuthUserViewTest(CourseTestCase):

    def test_view_login(self):
        url = reverse('website:login')
        response = self.client.get(url)

        # redirect to app academy
        self.assertEqual(response.status_code, 302)
