import csv
from io import StringIO

from django import forms
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.validators import FileExtensionValidator

from nolsatu_courses.apps.courses.models import Courses, Batch, Enrollment
from nolsatu_courses.apps import utils
from nolsatu_courses.apps.courses.utils import ImportCourse, ImportCourseError


class FormCourses(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if settings.FEATURE['MARKDOWN_BACKOFFICE_EDITOR']:
            self.fields.pop("short_description")
            self.fields.pop("description")
        else:
            self.fields.pop("short_description_md")
            self.fields.pop("description_md")

    class Meta:
        model = Courses
        exclude = ("users", "quizzes")


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


class FormBulkRegister(forms.Form):
    csv_file = forms.FileField(
        help_text=_("Pastikan kolom pertama berisi email/username"),
        validators=[FileExtensionValidator(allowed_extensions=['csv'])]
    )
    IDENTIFICATOR = (
        ('email', 'Email'),
        ('username', 'Username')
    )
    identificator = forms.ChoiceField(
        label=_("Idenfikator"), choices=IDENTIFICATOR, required=False)
    course = forms.ModelChoiceField(
        label=_("Kursus"), queryset=Courses.objects.all(),
        empty_label=_("Pilih Kursus")
    )
    batch = forms.ModelChoiceField(
        label=_("Angkatan"), queryset=Batch.objects.all(),
        empty_label=_("Pilih Angkatan")
    )
    allowed_access = forms.BooleanField(
        label=_("Beri akases"), required=False, initial=True,
        help_text=_("Jika Tidak, maka bisa memberikan akses secara manual")
    )

    def __init__(self, *args, **kwargs):
        self.reject_data = []
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        read_file = self.read_file()
        if len(next(read_file)) != 1:
            raise forms.ValidationError("Jumlah kolom yang diperbolehkan hanya 1")
        return cleaned_data

    def read_file(self):
        csvfile = self.cleaned_data['csv_file']
        csvfile.seek(0)
        decoded_file = csvfile.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)
        for row in reader:
            yield row

    def sync_users(self):
        data = self.read_file()
        for row in data:
            identificator = row[0].strip("")
            user = User.objects.filter(**self.get_identificator(identificator)).first()
            if user:
                self.register_course(user)
                continue
            else:
                resp = utils.get_user_academy(
                    type_identificator=self.cleaned_data['identificator'],
                    identificator=identificator
                )
                if resp.ok:
                    user = utils.update_user('', user=resp.json())
                    self.register_course(user)
                    continue
            self.reject_data.append(row)

        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)

        for row in self.reject_data:
            writer.writerow([
                row[0]
            ])
        return csv_buffer

    def get_identificator(self, identificator):
        if self.cleaned_data['identificator'] == 'email':
            return {'email': identificator}
        else:
            return {'username': identificator}

    def register_course(self, user):
        if self.cleaned_data['allowed_access']:
            status = Enrollment.STATUS.begin
        else:
            status = Enrollment.STATUS.register

        Enrollment.objects.update_or_create(
            user=user,
            course=self.cleaned_data['course'],
            batch=self.cleaned_data['batch'],
            defaults={
                'allowed_access': self.cleaned_data['allowed_access'],
                'status': status
            }
        )


class FormImportCourse(forms.Form):
    zip_file = forms.FileField(
        help_text=_("Unggah file .zip"),
        validators=[FileExtensionValidator(allowed_extensions=['zip'])]
    )

    def clean(self):
        cleaned_data = super().clean()
        imp_course = ImportCourse(cleaned_data['zip_file'])
        try:
            imp_course.prepare_data()
        except ImportCourseError as error:
            raise forms.ValidationError(f"Terjadi kesalahan: {error}")
        return cleaned_data

    def import_course(self):
        cleaned_data = super().clean()
        imp_course = ImportCourse(cleaned_data['zip_file'])
        imp_course.import_data()
