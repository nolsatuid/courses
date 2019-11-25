from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from nolsatu_courses.apps.courses.models import Courses


def details(request, slug):
    course = get_object_or_404(Courses, slug=slug)
    context = {
        'title': course.title,
        'course': course,
        'batch': course.get_last_batch(),
        'has_enrolled': course.has_enrolled(request.user)
    }
    return render(request, 'website/courses/details.html', context)


@login_required
def user_courses(request):
    enrolls = request.user.enroll.all()
    context = {
        'title': _('Daftar Kursusmu'),
        'courses': [enroll.course for enroll in enrolls]
    }
    return render(request, 'website/index.html', context)


@login_required
def enroll(request, slug):
    course = get_object_or_404(Courses, slug=slug)

    if course.has_enrolled(request.user):
        messages.success(request, _(f'Kamu sudah terdaftar di kelas {course.title}'))
        return redirect('website:courses:details', course.slug)

    if course.is_started():
        messages.warning(
            request, _(f'Gagal mendaftar, kelas {course.title} sudah dimulai')
        )
        return redirect('website:courses:details', course.slug)

    course.enrolled.create(course=course, user=request.user)
    messages.success(request, _(f'Kamu berhasil mendaftar pada kelas {course.title}'))
    return redirect('website:courses:details', course.slug)
