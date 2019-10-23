from django import forms
from nolsatu_courses.apps.courses.models import Courses


class FormCourses(forms.ModelForm):

    class Meta:
        model = Courses
        exclude = ("users",)
