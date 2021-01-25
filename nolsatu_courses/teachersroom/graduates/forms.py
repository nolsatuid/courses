from nolsatu_courses.apps.courses.models import Courses, Batch, Enrollment
from nolsatu_courses.backoffice.graduates.forms import FormFilterStudent


class TrainerFormFilterStudent(FormFilterStudent):
    def __init__(self, *args, **kwargs):
        user_email = kwargs.pop('user_email', None)
        super(TrainerFormFilterStudent, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = Courses.objects.filter(batchs__teaches__user__email=user_email)
        self.fields['batch'].queryset = Batch.objects.filter(teaches__user__email=user_email)
