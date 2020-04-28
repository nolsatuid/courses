from django import forms
from quiz.admin import QuizAdminForm


class FormQuiz(QuizAdminForm):

    class Media:
        css = {'all': ('admin/css/widgets.css',)}
        js = ('admin/jquery.js', '/admin/jsi18n/')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_time'].input_formats = ["%d-%m-%Y %H:%M"]
        self.fields['end_time'].input_formats = ["%d-%m-%Y %H:%M"]

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data['start_time']
        end_time = cleaned_data['end_time']

        if start_time and not end_time:
            raise forms.ValidationError("Waktu selesai harus diisi")
        elif not start_time and end_time:
            raise forms.ValidationError("Waktu awal harus diisi")
        elif start_time and end_time:
            if end_time.date() > start_time.date():
                raise forms.ValidationError(
                    "Tanggal waktu selesai tidak boleh lebih besar"
                    " dari tanggal waktu mulai")
            elif end_time.time() <= start_time.time():
                raise forms.ValidationError(
                    "Jam waktu selesai tidak boleh lebih kecil atau"
                    " sama dengan jam waktu mulai")

        return cleaned_data
