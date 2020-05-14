from django import forms
from model_utils import Choices
from django.utils.translation import ugettext_lazy as _
from nolsatu_courses.apps.courses.models import Section, CollectTask, Courses


class FormFilterTask(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Courses.objects.all(), empty_label="Pilih Kursus", required=False
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

        tasks = CollectTask.objects.select_related('section', 'user').all()
        if course:
            tasks = tasks.filter(section__module__course=course)

        if section:
            tasks = tasks.filter(section=section)

        if status:
            tasks = tasks.filter(status=status)

        self.tasks = tasks
        return self.tasks
