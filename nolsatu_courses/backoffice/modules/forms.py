from django import forms
from django.conf import settings

from nolsatu_courses.apps.courses.models import Module


class FormModule(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if settings.FEATURE['MARKDOWN_BACKOFFICE_EDITOR']:
            self.fields.pop("description")
        else:
            self.fields.pop("description_md")

    class Meta:
        model = Module
        exclude = ("course",)
