from django.utils.translation import ugettext_lazy as _

from django import forms
from django.conf import settings
from nolsatu_courses.apps.upload_files.models import UploadFile
from nolsatu_courses.apps.courses.models import CollectTask, TaskUploadSettings
import os


class FormUploadFile(forms.ModelForm):
    class Meta:
        model = UploadFile
        fields = ('file', 'name')
        widgets = {'name': forms.HiddenInput()}

    def __init__(self, section, user, *args, **kwargs):
        self.section = section
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['name'].widget = forms.TextInput(attrs={'value': 'File Tugas', 'hidden': True})

    def clean(self):
        cleaned_data = super().clean()
        upload_setting = TaskUploadSettings.objects.filter(section=self.section).first()
        if cleaned_data:
            if cleaned_data['file'].size > upload_setting.max_size*1048576:
                self.add_error('file', _(f"Ukuran file lebih dari {upload_setting.max_size}MB"))
            file_extension = os.path.splitext(str(cleaned_data['file']))[1]
            if str(file_extension) not in str(upload_setting.allowed_extension.all()):
                self.add_error('file', _(f"Ekstensi file tidak sesuai"))                
        return cleaned_data

    def save(self, collect_task):
        upload_file = super().save()

        # rename file upload
        ext = upload_file.file.name.split('.')[-1]
        initial_path = upload_file.file.path
        section_name = str(self.section).lower().replace(" ","")
        upload_file.file.name = f'uploads/{self.user.username}_{section_name}.{ext}'
        new_path = settings.MEDIA_ROOT + '/' + upload_file.file.name
        os.rename(initial_path, new_path)

        upload_file.name = f'File Tugas {self.user.username}-{self.section}'
        upload_file.save()

        if not collect_task:
            CollectTask.objects.create(section=self.section, user=self.user, file=upload_file)
