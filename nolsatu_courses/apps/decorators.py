import sweetify
import json

from functools import wraps

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import available_attrs
from django.utils.translation import ugettext_lazy as _
from django.http import Http404, HttpResponse
from django.contrib.auth.models import User

from nolsatu_courses.apps.courses.models import Module, Section
from nolsatu_courses.apps.accounts.models import MemberNolsatu


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
            sweetify.warning(
                request,
                'Peringatan', text=_("Maaf ya, kamu belum memiliki akses. Pastikan kamu sudah mendaftar"
                                     " dan admin telah menyetujui kamu sebagai peserta."), icon='warning', button='OK',
                timer=10000
            )
            return redirect('website:index')

        if not is_started or (enroll.date_limit_access < course.get_last_batch().start_date):
            sweetify.warning(
                request,
                'Peringatan', text=_("Maaf ya, kursus belum dimulai, pastikan kamu memulai kelas sesuai"
                                     " dengan tanggal mulai yang tertera."), icon='warning', button='OK',
                timer=10000
            )
            return redirect('website:courses:details', course.slug)

        if obj.has_enrolled(request.user) and enroll:
            if enroll.allowed_access:
                return view_func(request, *args, **kwargs)

        sweetify.warning(
            request,
            'Peringatan', text=_("Maaf ya, kamu belum memiliki akses. Pastikan kamu sudah mendaftar"
                                 " dan admin telah menyetujui kamu sebagai peserta."), icon='warning', button='OK',
            timer=10000
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


def vendor_member_required(a_func):
    """
    Decorator for views, that checks the vendor on nolsatu
    """

    @wraps(a_func, assigned=available_attrs(a_func))
    def _wrapped_view(request, *args, **kwargs):
        user = get_object_or_404(User, username=request.user, is_active=True, is_staff=True)

        if user.vendors.first() is None:
            raise Http404()

        return a_func(request, *args, **kwargs)

    return _wrapped_view


def ajax_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        response = json.dumps({'not_authenticated': True,
                               'message': 'Silakan Mendaftar Terlebih Dahulu atau Masuk Jika Telah Memiliki Akun'})
        return HttpResponse(response)

    return wrapper


def teacher_required(a_func):
    """
    Decorator for views, that checks the user on nolsatu
    """

    @wraps(a_func, assigned=available_attrs(a_func))
    def _wrapped_view(request, *args, **kwargs):
        user = get_object_or_404(User, username=request.user, is_active=True)
        if not user and user.nolsatu.role != MemberNolsatu.ROLE.trainer:
            raise Http404()
        return a_func(request, *args, **kwargs)

    return _wrapped_view
