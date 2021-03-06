from django import forms
from model_utils import Choices
from django.utils.translation import ugettext_lazy as _
from nolsatu_courses.apps.courses.models import Courses, Batch, Enrollment


class FormFilterStudent(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Courses.objects.all(), empty_label=_("Pilih Kursus"), required=False
    )
    batch = forms.ModelChoiceField(
        queryset=Batch.objects.all(), empty_label=_("Pilih Angkatan"), required=False
    )

    def get_data(self, status):
        students = Enrollment.objects.select_related(
            'course', 'user', 'batch', 'user__nolsatu'
        ).filter(status=status)
        course = self.cleaned_data['course']
        batch = self.cleaned_data['batch']

        if course:
            students = students.filter(course=course)

        if batch:
            students = students.filter(batch=batch)

        return students
