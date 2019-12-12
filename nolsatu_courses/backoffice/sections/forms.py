from django.utils.translation import ugettext_lazy as _

from django import forms
from nolsatu_courses.apps.courses.models import Section, TaskUploadSettings


class FormSection(forms.ModelForm):
    class Meta:
        model = Section
        exclude = ("module", "files",)


class FormTaskSetting(forms.ModelForm):
    class Meta:
        model = TaskUploadSettings
        fields = ("instruction","allowed_extension","max_size")

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data:
            for ext in cleaned_data['allowed_extension']:
                if not ext.startswith('.'):
                    self.add_error('allowed_extension', _(f"Ekstensi {ext} harus menggunakan titik didepan"))
        return cleaned_data
