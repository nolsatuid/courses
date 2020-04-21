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
            course=self.cleaned_data['course'], batch=self.cleaned_data['batch'],
            status__gte=Enrollment.STATUS.begin
        ).exclude(user__is_superuser=True)

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

    def get_quiz_stats(self):
        course = self.cleaned_data['course']
        quiz_stats = []

        for quiz in course.quizzes.prefetch_related('sitting_set'):
            sitting_stats = []
            count_pass = []
            count_not_pass = []
            perfect_score = []
            for sit in quiz.sitting_set.all():
                sitting_stats.append({
                    'sitting': sit,
                    'score': sit.get_percent_correct
                })

                # untuk mendapatkan jumlah lulus dan tidak lulus
                if sit.check_if_passed:
                    count_pass.append(sit.id)
                else:
                    count_not_pass.append(sit.id)

                # untuk mendapatkan peserta dengan nilai sempurta
                if sit.get_percent_correct == 100:
                    perfect_score.append(sit.id)

            # mendapatkan nilai tertinggi perserta dari quiz
            if sitting_stats:
                stats = max(sitting_stats, key=lambda s: s['score'])
            else:
                continue

            # tambahkan jumlah lulus tidak lulus
            stats.update({
                'pass': len(count_pass),
                'not_pass': len(count_pass),
                'perfect_score': len(perfect_score)
            })
            quiz_stats.append(stats)

        # tambahkan total lulus, tidak lulus, nilai sempurna
        sum_pass = sum(q['pass'] for q in quiz_stats)
        sum_not_pass = sum(q['not_pass'] for q in quiz_stats)
        sum_perfect_score = sum(q['perfect_score'] for q in quiz_stats)
        return {
            'detail_stats': quiz_stats,
            'sum_pass': sum_pass,
            'sum_not_pass': sum_not_pass,
            'sum_perfect_score': sum_perfect_score
        }
