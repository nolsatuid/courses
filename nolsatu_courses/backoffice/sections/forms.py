from django import forms
from nolsatu_courses.apps.courses.models import Section, TaskUploadSettings


class FormSection(forms.ModelForm):
    class Meta:
        model = Section
        exclude = ("module", "files",)

    def __init__(self, module=None, *args, **kwargs):
        self.module = module
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        section = super().save(commit=False)
        if self.module:
            section.module = self.module
        section.save()

        if not hasattr(section, 'task_setting'):
            task_setting = TaskUploadSettings(section=section, max_size="0")
            task_setting.save()

        return section


class FormTaskSetting(forms.ModelForm):
    class Meta:
        model = TaskUploadSettings
        fields = ("instruction","allowed_extension","max_size")
