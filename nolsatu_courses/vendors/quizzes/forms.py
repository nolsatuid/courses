from django import forms
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
