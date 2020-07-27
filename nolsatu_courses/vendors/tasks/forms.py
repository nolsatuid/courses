from django.db.models import Avg, F
from django.db.models.functions import Concat
from nolsatu_courses.apps.courses.models import (
    Section, CollectTask, Courses, Batch, Enrollment
)
from nolsatu_courses.backoffice.tasks.forms import FormFilterTask, FormFilterTaskReport


class FormFilterTaskVendor(FormFilterTask):
    def __init__(self, *args, **kwargs):
        self.tasks = None
        user_email = kwargs.pop('user_email', None)
        super(FormFilterTaskVendor, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = Courses.objects.filter(vendor__users__email=user_email)
        self.fields['batch'].queryset = Batch.objects.filter(course__vendor__users__email=user_email)
        self.fields['section'].queryset = Section.objects.filter(module__course__vendor__users__email=user_email)


class FormFilterTaskReportVendor(FormFilterTaskReport):
    def __init__(self, *args, **kwargs):
        self.tasks = None
        user_email = kwargs.pop('user_email', None)
        super(FormFilterTaskReportVendor, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = Courses.objects.filter(vendor__users__email=user_email)
        self.fields['batch'].queryset = Batch.objects.filter(course__vendor__users__email=user_email)

    def get_data(self):
        course = self.cleaned_data['course']
        batch = self.cleaned_data['batch']

        users_report_task = CollectTask.objects

        if course:
            users_report_task = users_report_task.filter(
                section__module__course=course
            )
        if batch:
            users_report_task = users_report_task.filter(user__enroll__batch=batch)

        users_report_result = users_report_task.values("section__module__course").annotate(
            name=Concat('user__first_name', 'user__last_name'), username=F("user__username"),
            avg_score=Avg("score"), title=F("section__module__course__title"))

        return users_report_result
