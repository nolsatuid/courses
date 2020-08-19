from nolsatu_courses.backoffice.forms import FormFilter
from nolsatu_courses.apps.courses.models import Courses, Batch


class FormFilterVendor(FormFilter):
    def __init__(self, *args, **kwargs):
        user_email = kwargs.pop('user_email', None)
        super(FormFilterVendor, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = Courses.objects.filter(vendor__users__email=user_email)
        self.fields['batch'].queryset = Batch.objects.filter(course__vendor__users__email=user_email)