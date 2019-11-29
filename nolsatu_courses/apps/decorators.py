from functools import wraps

from django.shortcuts import redirect
from django.utils.decorators import available_attrs
from django.core.exceptions import ObjectDoesNotExist

from nolsatu_courses.apps.courses.models import Courses, Module, Section


def enroll_required(view_func):
    """
    Decorator for views that checks that the user is has enrolled
    """
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        try:
            obj = Module.objects.get(slug=kwargs['slug'])
        except ObjectDoesNotExist:
            obj = Section.objects.get(slug=kwargs['slug'])

        if obj.has_enrolled(request.user):
            return view_func(request, *args, **kwargs)
        return redirect('website:index')
    return _wrapped_view
