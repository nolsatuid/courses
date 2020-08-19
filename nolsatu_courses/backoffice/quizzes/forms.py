import csv

from io import StringIO

from django import forms
from django.utils.translation import ugettext_lazy as _

from quiz.admin import QuizAdminForm
from multichoice.models import MCQuestion, Answer
from quiz.models import Quiz, Sitting, Question, SubCategory, Category
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

    def download_report(self):
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)

        enrolls = Enrollment.objects.filter(batch=self.cleaned_data['batch'])
        sittings = Sitting.objects.filter(user__id__in=enrolls.values_list('user__id', flat=True)) \
            .select_related('user', 'quiz')

        title = ['Nama Peserta']
        for quiz in self.get_data():
            title.append(quiz.title)
        writer.writerow(title)

        for enroll in enrolls:
            result = [f'{enroll.user.get_full_name()} ({enroll.user.username})']
            for quiz in self.get_data():
                score_quiz = sittings.filter(user=enroll.user, quiz=quiz)
                if score_quiz:
                    result.append(score_quiz.first().get_percent_correct)
                else:
                    result.append('0')
            writer.writerow(result)

        return csv_buffer


class CategoryFormBackoffice(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'


class MCQuestionFormBackoffice(forms.ModelForm):
    class Meta:
        model = MCQuestion
        fields = ('content', 'vendor', 'category', 'sub_category',
                  'figure', 'explanation', 'answer_order')
