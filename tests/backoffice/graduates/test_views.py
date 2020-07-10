from urllib.parse import urlencode

from tests import CourseTestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from nolsatu_courses.apps.courses.models import Enrollment


class GraduateViewTest(CourseTestCase):
    fixtures = [
        'courses.json', 'accounts.json', 'users.json', 'vendors.json',
        'upload_files.json'
    ]

    def setUp(self):
        super().setUp()
        user = User.objects.first()
        user.set_password('123qweasd')
        user.save()
        self.client.login(username=user.username, password='123qweasd')

    def test_candidate_to_graduate(self):
        enrollment = Enrollment.objects.last()
        self.assertIsNotNone(enrollment)

        # set admin to candidate user
        enrollment.status = Enrollment.STATUS.finish
        enrollment.finishing_date = timezone.now()
        enrollment.save()

        # initial score 0 and note None
        self.assertEqual(enrollment.final_score, 0)
        self.assertIsNone(enrollment.note)

        data = {
            'final_score': 88,
            'note': 'Mantul gan, kamu lulus dengan nilai tinggi'
        }
        query_params = urlencode(data)
        url = f"{reverse('backoffice:graduates:candidate_to_graduate', args=[enrollment.id])}?{query_params}"
        response = self.client.get(url)

        # redirect to candidate index
        self.assertRedirects(
            response, reverse('backoffice:graduates:candidate'),
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )

        # check status, final score and note
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.status, Enrollment.STATUS.graduate)
        self.assertEqual(enrollment.final_score, data['final_score'])
        self.assertEqual(enrollment.note, data['note'])
