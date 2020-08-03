from django import forms
from django.utils.translation import ugettext_lazy as _
from multichoice.models import MCQuestion, Answer
from quiz.models import Category, SubCategory


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


class AnswerForm(forms.Form):
    content = forms.CharField(label=_("Jawaban"), required=False)
    correct = forms.BooleanField(label=_("Jawaban Benar"), required=False)


class AnswerModelForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('content', 'correct')

    def save(self, question):
        answer = super().save(commit=False)
        answer.question = question
        answer.save()
