from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from nolsatu_courses.apps import utils
from nolsatu_courses.apps.courses.models import Courses, Enrollment


def details(request, slug):
    course = get_object_or_404(Courses, slug=slug)
    context = {
        'title': course.title,
        'course': course,
        'batch': course.get_last_batch(),
        'has_enrolled': course.has_enrolled(request.user),
        'enroll': course.get_enroll(request.user)
    }
    return render(request, 'website/courses/details.html', context)


@login_required
def user_courses(request):
    enrolls = request.user.enroll.all()

    context = {
        'title': _('Daftar Materimu'),
        'courses': [{
            "title": enroll.course.title,
            "short_description": enroll.course.short_description,
            "slug": enroll.course.slug,
            "featured_image": enroll.course.featured_image,
            "progress_precentage": int(enroll.course.progress_percentage(request.user))
        } for enroll in enrolls],
        'progress_bar': True
    }
    return render(request, 'website/index.html', context)


@login_required
def enroll(request, slug):
    course = get_object_or_404(Courses, slug=slug)

    if course.has_enrolled(request.user):
        messages.success(request, _(f'Kamu sudah terdaftar di kelas {course.title}'))
        return redirect('website:courses:details', course.slug)

    if not course.get_last_batch():
        messages.warning(
            request, _(f'Kelas {course.title} belum membuka pendaftaran')
        )
        return redirect('website:courses:details', course.slug)

    if course.is_started():
        messages.warning(
            request, _(f'Gagal mendaftar, kelas {course.title} sudah dimulai')
        )
        return redirect('website:courses:details', course.slug)

    course.enrolled.create(course=course, user=request.user, batch=course.batchs.last())
    messages.success(request, _(f'Kamu berhasil mendaftar pada kelas {course.title}'))
    utils.post_inbox(request, request.user, f'Kamu berhasil mendaftar di kelas {course.title}',
                     f'Saat ini kamu sudah berhasil mendaftar pada kelas {course.title}. Tunggu info selanjutnya ya.')
    return redirect('website:courses:details', course.slug)


@login_required
def finish(request, slug):
    course = get_object_or_404(Courses, slug=slug)

    # cek ketika belom menyelesaikan semua module dan bab.
    if course.progress_percentage(request.user, on_thousand=True) != 100:
        messages.warning(request, _(f'Kamu belom menyelesaikan semua materi {course.title}'))
        return redirect("website:courses:details", course.slug)

    enroll = Enrollment.objects.filter(course=course, user=request.user).first()
    enroll.status = Enrollment.STATUS.finish
    if not enroll.finishing_date:
        enroll.finishing_date = timezone.now().date()
        utils.post_inbox(request, request.user, f'Selamat!',
                         f'Selamat!, anda berhasil menyelesaikan kelas {enroll.course.title}')

    enroll.save()

    return redirect("website:courses:details", course.slug)
