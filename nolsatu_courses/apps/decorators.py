from functools import wraps

from django.shortcuts import redirect
from django.utils.decorators import available_attrs
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.courses.models import Courses, Module, Section


def enroll_required(view_func):
    """
    Decorator for views that checks that the user is has enrolled
    """
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        try:
            obj = Module.objects.get(slug=kwargs['slug'])
            allowed_access = obj.course.get_enroll(request.user).allowed_access
        except ObjectDoesNotExist:
            obj = Section.objects.get(slug=kwargs['slug'])
            allowed_access = obj.module.course.get_enroll(request.user).allowed_access

        if obj.has_enrolled(request.user) and allowed_access:
            return view_func(request, *args, **kwargs)

        messages.warning(
            request,
            _("Maaf ya, kamu belum memiliki akses. Pastikan kamu sudah mendaftar"
              " dan admin telah menyetujui kamu sebagai peserta.")
        )
        return redirect('website:index')
    return _wrapped_view
