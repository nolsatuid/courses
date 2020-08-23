from django import forms
from nolsatu_courses.apps.vendors.models import Vendor


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = "__all__"
