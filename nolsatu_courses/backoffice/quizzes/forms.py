import csv

from io import StringIO

from django import forms
from django.utils.translation import ugettext_lazy as _

from quiz.admin import QuizAdminForm
from quiz.models import Quiz, Sitting
from nolsatu_courses.apps.courses.models import Courses, Batch, Enrollment


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


class FormFilterQuizzes(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Courses.objects.all(), empty_label=_("Pilih Kursus")
    )
    batch = forms.ModelChoiceField(
        queryset=Batch.objects.all(), empty_label=_("Pilih Angkatan")
    )

    def get_data(self):
        quizzes = Quiz.objects.filter(courses=self.cleaned_data['course'])        

        return quizzes

    def download_report(self, batch):
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)
        
        users = Enrollment.objects.filter(batch=batch)  
        sittings = Sitting.objects.filter(
            user__id__in=users.values_list('user__id', flat=True)
            ).select_related('user', 'quiz')

        title = ['Nama Peserta']
        for quiz in self.get_data():
            title.append(quiz.title)
        writer.writeheader(title)
        
        for user in users:
            result = [f'{user.user.get_full_name()} ({user.user.username})']
            for quiz in self.get_data():                
                score_quiz = sittings.filter(user=user.user, quiz=quiz)
                if score_quiz:
                    result.append(score_quiz.first().get_percent_correct)
                else:
                    result.append('-')
            writer.writerow(result)

        return csv_buffer