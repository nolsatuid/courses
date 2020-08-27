from functools import wraps

from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import available_attrs
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.http import Http404
from django.contrib.auth.models import User

from nolsatu_courses.apps.courses.models import Courses, Module, Section


def enroll_required(view_func):
    """
    Decorator for views that checks that the user is has enrolled
    """

    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        module = Module.objects.select_related("course").filter(slug=kwargs['slug']).first()
        section = Section.objects.select_related("module", "module__course") \
            .filter(slug=kwargs['slug']).first()

        if not module and not section:
            raise Http404()

        if module:
            obj = module
            enroll = obj.course.get_enroll(request.user)
            course = obj.course
            is_started = course.is_started()
        else:
            obj = section
            enroll = obj.module.course.get_enroll(request.user)
            course = obj.module.course
            is_started = obj.module.course.is_started()

        if not enroll:
            messages.warning(
                request,
                _("Maaf ya, kamu belum memiliki akses. Pastikan kamu sudah mendaftar"
                  " dan admin telah menyetujui kamu sebagai peserta.")
            )
            return redirect('website:index')

        if not is_started or (enroll.date_limit_access < course.get_last_batch().start_date):
            messages.warning(
                request,
                _("Maaf ya, kursus belum dimulai, pastikan kamu memulai kelas sesuai"
                  " dengan tanggal <b>mulai</b> yang tertera.")
            )
            return redirect('website:courses:details', course.slug)

        if obj.has_enrolled(request.user) and enroll:
            if enroll.allowed_access:
                return view_func(request, *args, **kwargs)

        messages.warning(
            request,
            _("Maaf ya, kamu belum memiliki akses. Pastikan kamu sudah mendaftar"
              " dan admin telah menyetujui kamu sebagai peserta.")
        )
        return redirect('website:index')

    return _wrapped_view


def superuser_required(a_func):
    """
    Decorator for views, that checks the user on nolsatu
    """

    @wraps(a_func, assigned=available_attrs(a_func))
    def _wrapped_view(request, *args, **kwargs):
        user = get_object_or_404(User, username=request.user, is_active=True, is_superuser=True)
        if not user:
            raise Http404()
        return a_func(request, *args, **kwargs)
    return _wrapped_view
