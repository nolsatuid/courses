from urllib import request

from django.forms import ModelChoiceField
from nolsatu_courses.apps.courses.models import Courses
from nolsatu_courses.backoffice.batchs.forms import FormBatch


class FormBatchVendor(FormBatch):
    def __init__(self, *args, **kwargs):
        user_email = kwargs.pop('user_email', None)
        super(FormBatchVendor, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = Courses.objects.filter(vendor__users__email=user_email)
