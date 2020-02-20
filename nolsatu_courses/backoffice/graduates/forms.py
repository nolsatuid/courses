from django import forms
from model_utils import Choices
from django.utils.translation import ugettext_lazy as _
from nolsatu_courses.apps.courses.models import Courses, Batch


class FormFilterStudent(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Courses.objects.all(), empty_label="Pilih Kursus", required=False
    )
    batch = forms.ModelChoiceField(
        queryset=Batch.objects.all(), empty_label="Pilih Angkatan", required=False
    )

    def __init__(self, *args, **kwargs):
        self.graduate = None
        super().__init__(*args, **kwargs)

    def get_data(self, students):
        course = self.cleaned_data['course']
        batch = self.cleaned_data['batch']

        if course:
            students = students.filter(course=course)

        if batch:
            students = students.filter(batch=batch)

        self.students = students
        return self.students
