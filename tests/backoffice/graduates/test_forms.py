from urllib.parse import urlencode

from tests import CourseTestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from nolsatu_courses.apps.courses.models import Enrollment
from nolsatu_courses.backoffice.graduates.forms import FormFilterStudent


class GraduateFormTest(CourseTestCase):
    fixtures = [
        'courses.json', 'accounts.json', 'users.json', 'vendors.json',
        'upload_files.json'
    ]

    def test_form_filter_student(self):
        # get first enrollment then change status to finish
        enrollment = Enrollment.objects.first()
        enrollment.status = Enrollment.STATUS.finish
        enrollment.save()

        data = {
            'course': enrollment.course.id,
            'batch': enrollment.batch.id
        }

        # test filter user enroll status finish
        form = FormFilterStudent(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.get_data(Enrollment.STATUS.finish).count(), 1
        )

        # change all status to finish
        Enrollment.objects.all() \
            .update(status=Enrollment.STATUS.finish)

        # test find user graduate, but not found
        form = FormFilterStudent(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.get_data(Enrollment.STATUS.graduate).count(), 0
        )
