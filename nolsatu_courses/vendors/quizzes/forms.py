from django import forms

from quiz.models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ('vendor',)

