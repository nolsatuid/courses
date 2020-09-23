import sweetify
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Prefetch

from nolsatu_courses.apps import utils
from nolsatu_courses.apps.courses.models import Courses, Enrollment, Module, Section, CollectTask
from quiz.models import Quiz, Sitting


def details(request, slug):
    if request.user.is_superuser:
        course = get_object_or_404(
            Courses.objects.prefetch_related(
                Prefetch('modules', queryset=Module.objects.publish()),
                Prefetch('modules__sections', queryset=Section.objects.publish())
            ).select_related('vendor'),
            slug=slug
        )
    else:
        course = get_object_or_404(
            Courses.objects.prefetch_related(
                Prefetch('modules', queryset=Module.objects.publish()),
                Prefetch('modules__sections', queryset=Section.objects.publish())
            ).select_related('vendor'),
            slug=slug, status=Courses.STATUS.publish
        )

    context = {
        'title': course.title,
        'course': course,
        'batch': course.get_last_batch(),
        'has_enrolled': course.has_enrolled(request.user),
        'enroll': course.get_enroll(request.user),
        'meta': course.as_meta()
    }

    return render(request, 'website/courses/details.html', context)


@login_required
def user_courses(request):
    enrolls = request.user.enroll.filter(batch__isnull=False).select_related("course")

    context = {
        'title': _('Daftar Materimu'),
        'courses': [{
            "course": enroll.course,
            "progress_precentage": int(enroll.course.progress_percentage(request.user)),
            "progress_step": f'{enroll.course.number_of_activity_step(request.user)} dari {enroll.course.number_of_step()}',
            "status_enroll": enroll.status,
            "final_score": enroll.final_score,
            "note": enroll.note
        } for enroll in enrolls],
        'user_page': True
    }
    return render(request, 'website/user/courses.html', context)


@login_required
def user_quizzes(request, course_id):
    course = get_object_or_404(Courses, id=course_id)
    quizzes = Quiz.objects.filter(courses=course)
    sittings = Sitting.objects.filter(user=request.user, quiz_id__in=quizzes) \
        .select_related('user', 'quiz')

    context = {
        'title': _(f'Kursus: {course.title}'),
        'sittings': sittings,
        'user_page': True
    }
    return render(request, 'website/user/quizzes.html', context)


@login_required
def user_tasks(request, course_id):
    course = get_object_or_404(Courses, id=course_id)
    tasks = CollectTask.objects.select_related(
        'section', 'file', 'section__module__course'
    ).filter(section__module__course=course, user=request.user)

    context = {
        'title': _(f'Kursus: {course.title}'),
        'tasks': tasks,
        'user_page': True
    }
    return render(request, 'website/user/tasks.html', context)


@login_required
def enroll(request, slug):
    course = get_object_or_404(Courses, slug=slug)

    if course.has_enrolled(request.user):
        sweetify.success(
            request, _(f'Kamu sudah terdaftar di kelas {course.title}'),
            button='OK', icon='success', timer=10000
        )
        return redirect('website:courses:details', course.slug)

    if not course.get_last_batch():
        sweetify.warning(
            request, _(f'Kelas {course.title} belum membuka pendaftaran',
            button='OK', icon='warning', timer=10000)
        )
        return redirect('website:courses:details', course.slug)

    if course.is_started():
        sweetify.warning(
            request, _(f'Gagal mendaftar, kelas {course.title} sudah dimulai'),
            button='OK', icon='warning', timer=10000
        )
        return redirect('website:courses:details', course.slug)

    course.enrolled.create(course=course, user=request.user, batch=course.batchs.last())
    sweetify.success(
        request, _(f'Kamu berhasil mendaftar pada kelas {course.title}'), 
        button='OK', icon='success', timer=10000
    )
    utils.send_notification(
        request.user,
        f'Kamu berhasil mendaftar di kelas {course.title}',
        f'Saat ini kamu sudah berhasil mendaftar pada kelas {course.title}. Tunggu info selanjutnya ya.'
    )
    return redirect('website:courses:details', course.slug)


@login_required
def finish(request, slug):
    course = get_object_or_404(Courses, slug=slug)

    # cek ketika belom menyelesaikan semua module dan bab.
    if course.progress_percentage(request.user, on_thousand=True) != 100:
        sweetify.warning(
            request, _(f'Kamu belom menyelesaikan semua materi {course.title}'), 
            button='OK', icon='warning', timer=10000
        )
        return redirect("website:courses:details", course.slug)

    enroll = Enrollment.objects.filter(course=course, user=request.user).first()
    enroll.status = Enrollment.STATUS.finish
    if not enroll.finishing_date:
        enroll.finishing_date = timezone.now().date()
        utils.send_notification(request.user, f'Selamat!',
                         f'Selamat!, anda berhasil menyelesaikan kelas {enroll.course.title}')

    enroll.save()

    return redirect("website:courses:details", course.slug)
