import sweetify

from functools import wraps

from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import available_attrs
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from .models import Quiz, Sitting, Question


def quiz_access_required(view_func):
    """
    Decorator for views that checks that the user has enroll on the course
    and the quiz is part of the course
    """
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        quiz_name = kwargs['quiz_name'] if 'quiz_name' in kwargs else kwargs['slug']
        quiz = get_object_or_404(Quiz.objects.select_related(), url=quiz_name)

        # apa bila memiliki jadwal
        if quiz.any_schedule():
            if timezone.now() < quiz.start_time:
                sweetify.warning(
                    request, _(f"{quiz.title} hasn't started yet"),
                    button='OK', icon='warning', timer=10000
                )
                return redirect('website:index')
            elif timezone.now() > quiz.end_time:
                finish_out_time(quiz, request.user)
                sweetify.warning(
                    request, _(f"{quiz.title} is over"),
                    button='OK', icon='warning', timer=10000
                )
                return redirect('website:index')

        courses = quiz.courses_set.all()
        for course in courses:
            if course.has_enrolled(request.user):
                return view_func(request, *args, **kwargs)

        sweetify.warning(
            request,
            _(f"You are not registered on the quiz <strong> {quiz.title} </strong>"),
            button='OK', icon='warning', timer=10000
        )
        return redirect('website:index')
    return _wrapped_view


def finish_out_time(quiz, user):
    """
    fungsi ini untuk menyelesaikan quiz jika waktu sudah habis
    """
    sitting = Sitting.objects.user_sitting(user, quiz)
    if sitting:
        # ambil pertanyaan yang belom dibuka, lalu tambahkan
        # kedalam jawaban salah
        q_ids = sitting.question_list.strip(",").split(",")
        questions = Question.objects.filter(id__in=q_ids)
        for q in questions:
            sitting.add_incorrect_question(q)

        # tandai bahwa quiz sudah selesai
        sitting.mark_quiz_complete(out_time=True)
