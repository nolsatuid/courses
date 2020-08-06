from django import forms
from multichoice.models import MCQuestion, Answer
from quiz.models import Category, SubCategory, Question
from nolsatu_courses.backoffice.quizzes.forms import FormQuiz, FormFilterQuizzes
from nolsatu_courses.apps.courses.models import Courses, Batch


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ('vendor',)


class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        exclude = ('category',)


class MCQuestionForm(forms.ModelForm):
    class Meta:
        model = MCQuestion
        fields = ('content', 'category', 'sub_category',
                  'figure', 'explanation', 'answer_order')

    def save(self, vendor):
        question = super().save(commit=False)
        question.vendor = vendor
        question.save()
        return question


class FormQuizVendor(FormQuiz):
    def __init__(self, *args, **kwargs):
        user_email = kwargs.pop('user_email', None)
        super(FormQuizVendor, self).__init__(*args, **kwargs)
        self.fields['start_time'].input_formats = ["%d-%m-%Y %H:%M"]
        self.fields['end_time'].input_formats = ["%d-%m-%Y %H:%M"]
        self.fields['category'].queryset = Category.objects.filter(vendor__users__email=user_email)
        self.fields['courses'].queryset = Courses.objects.filter(vendor__users__email=user_email)
        self.fields['questions'].queryset = Question.objects.filter(vendor__users__email=user_email)


class FormFilterQuizzesVendor(FormFilterQuizzes):
    def __init__(self, *args, **kwargs):
        user_email = kwargs.pop('user_email', None)
        super(FormFilterQuizzesVendor, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = Courses.objects.filter(vendor__users__email=user_email)
        self.fields['batch'].queryset = Batch.objects.filter(course__vendor__users__email=user_email)
