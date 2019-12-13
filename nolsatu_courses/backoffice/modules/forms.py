from django import forms
from nolsatu_courses.apps.courses.models import Module


class FormModule(forms.ModelForm):

    class Meta:
        model = Module
        exclude = ("course",)