from django import forms
from django.utils.translation import ugettext_lazy as _
from nolsatu_courses.apps.courses.models import (
    Section, Courses, Batch, )
from nolsatu_courses.backoffice.tasks.forms import FormFilterTask


class TrainerFormFilterTask(FormFilterTask):

    def __init__(self, *args, **kwargs):
        user_email = kwargs.pop('user_email', None)
        self.tasks = None
        super(TrainerFormFilterTask, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = Courses.objects.filter(batchs__teaches__user__email=user_email)
        self.fields['batch'].queryset = Batch.objects.filter(teaches__user__email=user_email)