import csv

from io import StringIO

from django import forms
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from model_utils import Choices
from django.utils.translation import ugettext_lazy as _
from nolsatu_courses.apps.courses.models import (
    Section, CollectTask, Courses, Batch, Enrollment
)


class FormFilterTask(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Courses.objects.all(), empty_label="Pilih Kursus",
    )
    batch = forms.ModelChoiceField(
        queryset=Batch.objects.all(), empty_label=_("Pilih Angkatan"), required=False
    )
    section = forms.ModelChoiceField(
        queryset=Section.objects.all(), empty_label="Pilih Bab", required=False
    )
    STATUS = Choices(
        ('', '', _('Pilih Status')),
        (1, 'review', _('Diperiksa')),
        (2, 'repeat', _('Mengulang')),
        (4, 'not_pass', _('Tidak Lulus')),
        (3, 'graduated', _('Lulus')),
    )
    status = forms.ChoiceField(choices=STATUS, required=False, label="Status")

    def __init__(self, *args, **kwargs):
        self.tasks = None
        super().__init__(*args, **kwargs)

    def get_data(self):
        course = self.cleaned_data['course']
        section = self.cleaned_data['section']
        status = self.cleaned_data['status']
        batch = self.cleaned_data['batch']

        tasks = CollectTask.objects.select_related(
            'section', 'user', 'file', 'section__module__course'
        ).all()

        if course:
            tasks = tasks.filter(section__module__course=course)

        if section:
            tasks = tasks.filter(section=section)

        if batch:
            user_ids = Enrollment.objects.filter(batch=batch).values_list('user__id', flat=True)
            tasks = tasks.filter(user__id__in=user_ids)

        if status:
            tasks = tasks.filter(status=status)

        self.tasks = tasks
        return self.tasks


class FormFilterTaskReport(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Courses.objects.all(), empty_label="Pilih Kursus",
    )
    batch = forms.ModelChoiceField(
        queryset=Batch.objects.all(), empty_label=_("Pilih Angkatan"), required=False
    )

    def __init__(self, *args, **kwargs):
        self.tasks = None
        super().__init__(*args, **kwargs)

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

        return users, avg_score

    def download_report(self):
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)

        course = self.cleaned_data['course']
        enrollment = Enrollment.objects.filter(course=course, batch=self.cleaned_data['batch']).select_related('user')
        # write course name, users
        writer.writerow([f"Kursus: {course.title}"] + list(map(lambda e: e.user.get_full_name(), enrollment)))

        for module in course.modules.order_by('order'):
            # Write modules row
            writer.writerow([f'Modul: {module.title}'])
            for section in module.sections.filter(is_task=True).order_by('order'):
                section_row = [section.title]
                collect_task = CollectTask.objects.filter(section=section).values("user", "score")
                collect_task = {d['user']: d['score'] for d in collect_task}
                for e in enrollment:
                    section_row.append(collect_task.get(e.user.id, 0))

                # write section
                writer.writerow(section_row)

        return csv_buffer
