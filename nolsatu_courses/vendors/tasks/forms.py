from nolsatu_courses.apps.courses.models import (
    Section, CollectTask, Courses, Batch, Enrollment
)
from nolsatu_courses.backoffice.tasks.forms import FormFilterTask


class FormFilterTaskVendor(FormFilterTask):
    def __init__(self, *args, **kwargs):
        self.tasks = None
        user_email = kwargs.pop('user_email', None)
        super(FormFilterTaskVendor, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = Courses.objects.filter(vendor__users__email=user_email)
        self.fields['batch'].queryset = Batch.objects.filter(course__vendor__users__email=user_email)
        self.fields['section'].queryset = Section.objects.filter(module__course__vendor__users__email=user_email)