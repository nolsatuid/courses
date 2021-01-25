from nolsatu_courses.apps.accounts.models import MemberNolsatu
from operator import itemgetter, attrgetter

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from nolsatu_courses.backoffice.graduates.forms import FormFilterStudent
from nolsatu_courses.apps.courses.models import Batch, Courses, Enrollment, Teach


class FormFilter(FormFilterStudent):
    def __init__(self, user, *args, **kwargs):
        self.progresses = []
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['batch'].required = True
        self.fields['course'].required = True
        
        self.fields['batch'].queryset = self.get_batch_choice()
        self.fields['course'].queryset = self.get_courses_choice()

    def get_data(self):
        self.enrolls = Enrollment.objects.select_related('course', 'user').filter(
            course=self.cleaned_data['course'], batch=self.cleaned_data['batch'],
            status__gte=Enrollment.STATUS.begin
        ).exclude(user__is_superuser=True)

        data = []
        for enroll in self.enrolls:
            progress = self.cleaned_data['course'].progress_percentage(enroll.user)
            self.progresses.append(progress)
            data.append({
                'user': enroll.user,
                'progress': progress,
                'number_of_activity_step': self.cleaned_data['course'].number_of_activity_step(enroll.user),
                'task': enroll.get_count_task_status()
            })

        return sorted(data, key=lambda value: value['progress'], reverse=True)

    def get_batch_choice(self):
        if self.user and self.user.nolsatu.role == MemberNolsatu.ROLE.trainer:
            batch_ids = Teach.objects.filter(user=self.user).values_list('batch', flat=True)
            return Batch.objects.filter(pk__in=batch_ids)

    def get_courses_choice(self):
        if self.user and self.user.nolsatu.role == MemberNolsatu.ROLE.trainer:
            batch_ids = Teach.objects.filter(user=self.user).values_list('batch', flat=True)
            courses_ids = Batch.objects.values_list('course', flat=True).filter(pk__in=batch_ids).distinct()
            return Courses.objects.filter(pk__in=courses_ids)

    def global_progress(self):
        try:
            return sum(self.progresses) / len(self.progresses)
        except ZeroDivisionError:
            return 0

    def get_quiz_stats(self):
        course = self.cleaned_data['course']
        quiz_stats = []

        user_ids = self.enrolls.values_list('user__id', flat=True)

        for quiz in course.quizzes.prefetch_related('sitting_set'):
            sitting_stats = []
            count_pass = []
            count_not_pass = []
            perfect_score = []
            for sit in quiz.sitting_set.filter(user__in=user_ids):
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
                'not_pass': len(count_not_pass),
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
