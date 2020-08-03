from django import forms

from quiz.models import Category, SubCategory


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ('vendor',)


class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        exclude = ('category',)
