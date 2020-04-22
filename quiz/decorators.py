from functools import wraps

from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import available_attrs
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.courses.models import Courses
from .models import Quiz


def quiz_access_required(view_func):
    """
    Decorator for views that checks that the user has enroll on the course
    and the quiz is part of the course
    """
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        quiz_name = kwargs['quiz_name'] if 'quiz_name' in kwargs else kwargs['slug']
        quiz = get_object_or_404(Quiz, url=quiz_name)
        courses = Courses.objects.filter(quizzes=quiz)
        for course in courses:
            course.has_enrolled(request.user)
            return view_func(request, *args, **kwargs)

        messages.warning(
            request,
            _(f"Kamu tidak terdaftar pada kuis <strong> {quiz.title} </strong>")
        )
        return redirect('website:index')
    return _wrapped_view
