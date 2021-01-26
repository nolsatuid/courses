from django import forms
from django.contrib.auth.models import User
from django.db.models import Avg
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.courses.models import (
    Courses, Batch, CollectTask, )
from nolsatu_courses.backoffice.tasks.forms import FormFilterTask, FormFilterTaskReport


class TrainerFormFilterTask(FormFilterTask):

    def __init__(self, *args, **kwargs):
        user_email = kwargs.pop('user_email', None)
        self.tasks = None
        super(TrainerFormFilterTask, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = Courses.objects.filter(batchs__teaches__user__email=user_email)
        self.fields['batch'].queryset = Batch.objects.filter(teaches__user__email=user_email)


class TrainerFormFilterTaskReport(FormFilterTaskReport):
    batch = forms.ModelChoiceField(
        queryset=Batch.objects.all(), empty_label=_("Pilih Angkatan"))

    def get_data(self):
        course = self.cleaned_data['course']
        batch = self.cleaned_data['batch']

        users = User.objects

        if course:
            users = users.filter(enroll__course=course)

        if batch:
            users = users.filter(enroll__batch=batch)

        avg_score = CollectTask.objects.filter(
            section__module__course=course
        ).values("user").annotate(avg_score=Avg("score"))

        avg_score = {d['user']: d['avg_score'] for d in avg_score}

        return users, avg_score, batch

    def __init__(self, *args, **kwargs):
        user_email = kwargs.pop('user_email', None)
        self.tasks = None
        super(FormFilterTaskReport, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = Courses.objects.filter(batchs__teaches__user__email=user_email)
        self.fields['batch'].queryset = Batch.objects.filter(teaches__user__email=user_email)
