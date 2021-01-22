from django import forms
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.backoffice.quizzes.forms import FormFilterQuizzes
from quiz.models import Quiz
from nolsatu_courses.apps.courses.models import Courses, Batch


class TrainerFormFilterQuizzes(FormFilterQuizzes):
    def get_data(self):
        quizzes = Quiz.objects.filter(courses=self.cleaned_data['course'])

        return quizzes

    def __init__(self, *args, **kwargs):
        user_email = kwargs.pop('user_email', None)
        super(TrainerFormFilterQuizzes, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = Courses.objects.filter(batchs__teaches__user__email=user_email)
        self.fields['batch'].queryset = Batch.objects.filter(teaches__user__email=user_email)
