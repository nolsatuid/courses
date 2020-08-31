from django import forms
from nolsatu_courses.apps.products.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
