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
            obj = Module.objects.select_related("course").get(slug=kwargs['slug'])
            enroll = obj.course.get_enroll(request.user)
            course = obj.course
            is_started = course.is_started()
        except ObjectDoesNotExist:
            obj = Section.objects.select_related("module", "module__course") \
                .get(slug=kwargs['slug'])
            enroll = obj.module.course.get_enroll(request.user)
            course = obj.module.course
            is_started = obj.module.course.is_started()

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
