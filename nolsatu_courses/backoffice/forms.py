from operator import itemgetter, attrgetter

from nolsatu_courses.backoffice.graduates.forms import FormFilterStudent
from nolsatu_courses.apps.courses.models import Enrollment


class FormFilter(FormFilterStudent):
    def __init__(self, *args, **kwargs):
        self.progresses = []
        super().__init__(*args, **kwargs)
        self.fields['batch'].required = True
        self.fields['course'].required = True

    def get_data(self):
        enrolls = Enrollment.objects.select_related('course', 'user').filter(
            course=self.cleaned_data['course'], batch=self.cleaned_data['batch']
        )

        data = []
        for enroll in enrolls:
            progress = self.cleaned_data['course'].progress_percentage(enroll.user)
            self.progresses.append(progress)
            data.append({
                'user': enroll.user,
                'progress': progress,
                'number_of_activity_step': self.cleaned_data['course'].number_of_activity_step(enroll.user),
                'task': enroll.get_count_task_status()
            })

        return sorted(data, key=lambda value: value['progress'], reverse=True)

    def global_progress(self):
        try:
            return sum(self.progresses) / len(self.progresses)
        except ZeroDivisionError:
            return 0
