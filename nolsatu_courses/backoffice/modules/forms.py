from django import forms
from nolsatu_courses.apps.courses.models import Module


class FormModule(forms.ModelForm):

    class Meta:
        model = Module
        fields = ('title', 'description', 'order','is_visible')

    def __init__(self, course=None, *args, **kwargs):
        self.course = course
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        module = super().save(commit=False)
        if self.course:
            module.course = self.course
        module.save()
        return module