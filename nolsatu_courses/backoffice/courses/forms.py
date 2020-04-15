from django import forms
from django.utils.translation import ugettext_lazy as _
from nolsatu_courses.apps.courses.models import Courses, Batch


class FormCourses(forms.ModelForm):

    class Meta:
        model = Courses
        exclude = ("users",)


class FormFilterRegistrants(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Courses.objects.all(), empty_label=_("Pilih Kursus"), required=False
    )
    batch = forms.ModelChoiceField(
        queryset=Batch.objects.all(), empty_label=_("Pilih Angkatan"), required=False
    )

    def get_data(self, registrants):
        course = self.cleaned_data['course']
        batch = self.cleaned_data['batch']

        if course:
            registrants = registrants.filter(course=course)

        if batch:
            registrants = registrants.filter(batch=batch)

        return registrants