from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from nolsatu_courses.apps import utils
from nolsatu_courses.apps.courses.models import Courses, Enrollment
from nolsatu_courses.vendors.courses.forms import (FormVendorCourse,
                                                   FormFilterRegistrantsVendors, )


@staff_member_required
def index(request):
    context = {
        'courses': Courses.objects.filter(vendor__users__email=request.user.email),
        'menu_active': 'course',
        'title': _('Daftar Kursus'),
        'sidebar': True
    }
    return render(request, 'vendors/courses/list.html', context)


@staff_member_required
def details(request, courses_id):
    course = get_object_or_404(Courses, id=courses_id, vendor__users__email=request.user.email)
    context = {
        'menu_active': 'course',
        'title': 'Detail Kursus',
        'course': course,
    }
    return render(request, 'vendors/courses/detail.html', context)


@staff_member_required
def create(request):
    template_name = 'vendors/form-editor.html'

    form = FormVendorCourse(data=request.POST or None, files=request.FILES or None)
    author = User.objects.filter(email=request.user.email).first()

    if form.is_valid():
        with transaction.atomic():
            course = form.save(author)
            form.save_m2m()
            messages.success(request, _(f"Berhasil tambah kursus {course.title}"))
        return redirect('vendors:courses:index')

    context = {
        'menu_active': 'course',
        'title': _('Tambah Kursus'),
        'form': form,
        'title_submit': 'Simpan'
    }

    if settings.FEATURE["MARKDOWN_VENDORS_EDITOR"]:
        template_name = 'vendors/form-editor-markdown.html'

    return render(request, template_name, context)


@staff_member_required
def delete(request, id):
    course = get_object_or_404(Courses, id=id, vendor__users__email=request.user.email)
    course.delete()
    messages.success(request, 'Berhasil hapus kursus')
    return redirect('vendors:courses:index')


@staff_member_required
def edit(request, id):
    template_name = 'vendors/form-editor.html'
    course = get_object_or_404(Courses, id=id, vendor__users__email=request.user.email)
    author = User.objects.filter(email=request.user.email).first()
    form = FormVendorCourse(data=request.POST or None, files=request.FILES or None, instance=course)

    if form.is_valid():
        with transaction.atomic():
            change_course = form.save(author)
            form.save_m2m()
        messages.success(request, _(f"Berhasil ubah kursus {change_course.title}"))
        return redirect('vendors:courses:index')

    context = {
        'menu_active': 'course',
        'title': _('Ubah Kursus'),
        'form': form,
        'title_submit': 'Simpan'
    }

    if settings.FEATURE["MARKDOWN_VENDORS_EDITOR"]:
        template_name = 'vendors/form-editor-markdown.html'

    return render(request, template_name, context)


@staff_member_required
def registrants(request):
    template_name = 'vendors/courses/registrants.html'
    list_registrants = Enrollment.objects.filter(course__vendor__users__email=request.user.email,
                                                 ).select_related('user', 'course', 'batch')
    form = FormFilterRegistrantsVendors(request.GET or None, user_email=request.user.email)
    if form.is_valid():
        list_registrants = form.get_data(registrants=list_registrants)

    if request.POST:
        data = request.POST
        if data.getlist('checkMark'):
            for id in data.getlist('checkMark'):
                enroll = get_object_or_404(Enrollment, id=id, course__vendor__users__email=request.user.email)
                if settings.COURSE_CONFIGS['REQUIRED_LINK_GROUP'] and \
                        not enroll.course.batchs.last().link_group:
                    messages.error(
                        request,
                        _(
                            f'Gagal mengubah status <strong>{enroll}</strong>, karena link grup pada batch {enroll.batch} belum diisi')
                    )
                else:
                    if enroll.batch != enroll.course.batchs.last():
                        enroll.batch = enroll.course.batchs.last()
                    enroll.allowed_access = True
                    enroll.status = Enrollment.STATUS.begin
                    enroll.save()

                    text1 = f'Selamat, Anda sudah mendapatkan akses kelas {enroll.course.title}. '
                    text2 = f'Gabung ke grup chat menggunakan link <a href="{enroll.batch.link_group}">ini</a> untuk ' \
                            f'mendapatkan informasi lebih lanjut. '
                    notif_msg = text1 + text2 if settings.COURSE_CONFIGS['REQUIRED_LINK_GROUP'] else text1

                    utils.send_notification(
                        enroll.user, f'Akses kelas {enroll.course.title} di berikan', notif_msg)

            messages.success(request, _(f'Berhasil memberikan akses massal'))

    context = {
        'menu_active': 'registrants',
        'title': _('Pendaftar Kursus'),
        'registrants': list_registrants,
        'form': form
    }
    return render(request, template_name, context)


@staff_member_required
def ajax_change_status_registrants(request):
    id = request.GET.get('id', None)
    status = request.GET.get('status', None)
    enroll = get_object_or_404(Enrollment, id=id, course__vendor__users__email=request.user.email)
    if settings.COURSE_CONFIGS['REQUIRED_LINK_GROUP'] and \
            not enroll.course.batchs.last().link_group:
        data = {
            'status': False,
            'message': f'Link grup pada batch {enroll.batch} belum diisi',
            'batch': enroll.batch.batch
        }
        return JsonResponse(data, status=200)
    if enroll.batch != enroll.course.batchs.last():
        enroll.batch = enroll.course.batchs.last()
    enroll.allowed_access = status
    enroll.status = Enrollment.STATUS.begin
    with transaction.atomic():
        enroll.save()

    if status == "True":
        text1 = f'Selamat, Anda sudah mendapatkan akses kelas {enroll.course.title}. '
        text2 = f'Gabung ke grup chat menggunakan link <a href="{enroll.batch.link_group}">ini</a> untuk mendapatkan informasi lebih lanjut.'
        notif_msg = text1 + text2 if settings.COURSE_CONFIGS['REQUIRED_LINK_GROUP'] else text1
        utils.send_notification(enroll.user, f'Akses kelas {enroll.course.title} di berikan', notif_msg)
    else:
        utils.send_notification(enroll.user, f'Akses kelas {enroll.course.title} dibatalkan',
                                f'Maaf, Akses belajar pada kelas {enroll.course.title} Anda dibatalkan.')

    data = {
        'status': True,
        'message': f'Berhasil mengubah hak akses {enroll.user.get_full_name()}',
        'batch': enroll.batch.batch,
        'detail': f'{enroll.user.get_full_name()} - {enroll.course}'
    }
    return JsonResponse(data, status=200)

