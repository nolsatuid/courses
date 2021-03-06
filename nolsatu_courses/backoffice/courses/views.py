import sweetify

from django.conf import settings
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db.models import Prefetch

from nolsatu_courses.apps import utils
from nolsatu_courses.apps.courses.models import Courses, Enrollment, Module, Section
from nolsatu_courses.apps.courses.utils import ExportCourse
from nolsatu_courses.apps.decorators import superuser_required
from .forms import FormCourses, FormFilterRegistrants, FormBulkRegister, FormImportCourse


@superuser_required
def index(request):
    context = {
        'menu_active': 'course',
        'title': _('Daftar Kursus'),
        'courses': Courses.objects.all(),
        'sidebar': True
    }
    return render(request, 'backoffice/courses/index.html', context)


@superuser_required
def add(request):
    form = FormCourses(data=request.POST or None, files=request.FILES or None)
    if form.is_valid():
        course = form.save()
        sweetify.success(request, _(f"Berhasil tambah kursus {course.title}"), button='OK', icon='success')
        return redirect('backoffice:courses:index')

    context = {
        'menu_active': 'course',
        'title': _('Tambah Kursus'),
        'form': form,
        'title_submit': 'Simpan'
    }

    template = 'backoffice/form-editor.html'
    if settings.FEATURE["MARKDOWN_BACKOFFICE_EDITOR"]:
        template = 'backoffice/form-editor-markdown.html'

    return render(request, template, context)


@superuser_required
def edit(request, id):
    course = get_object_or_404(Courses, id=id)
    form = FormCourses(data=request.POST or None, files=request.FILES or None, instance=course)
    if form.is_valid():
        course = form.save()
        sweetify.success(request, _(f"Berhasil ubah kursus {course.title}"), button='OK', icon='success')
        return redirect('backoffice:courses:index')

    context = {
        'menu_active': 'course',
        'title': _('Ubah Kursus'),
        'form': form,
        'title_submit': 'Simpan'
    }

    template = 'backoffice/form-editor.html'
    if settings.FEATURE["MARKDOWN_BACKOFFICE_EDITOR"]:
        template = 'backoffice/form-editor-markdown.html'

    return render(request, template, context)


@superuser_required
def delete(request, id):
    course = get_object_or_404(Courses, id=id)
    course.delete()
    sweetify.success(request, 'Berhasil hapus kursus', button='OK', icon='success')
    return redirect('backoffice:courses:index')


@superuser_required
def details(request, id):
    course = get_object_or_404(Courses, id=id)

    context = {
        'menu_active': 'course',
        'title': 'Detail Kursus',
        'course': course
    }
    return render(request, 'backoffice/courses/detail.html', context)


@superuser_required
def registrants(request):
    registrants = Enrollment.objects.select_related('user', 'course', 'batch')
    form = FormFilterRegistrants(request.GET or None)
    if form.is_valid():
        registrants = form.get_data(registrants=registrants)

    if request.POST:
        data = request.POST
        if data.getlist('checkMark'):
            for id in data.getlist('checkMark'):
                enroll = get_object_or_404(Enrollment, id=id)
                if settings.COURSE_CONFIGS['REQUIRED_LINK_GROUP'] and \
                        not enroll.course.batchs.last().link_group:
                    sweetify.error(
                        request,
                        'Gagal', text=_(f'Gagal mengubah status <strong>{enroll}</strong>, karena link grup pada batch {enroll.batch} belum diisi'),
                        button='OK', timer=10000, icon='error'
                    )
                else:
                    enroll.allowed_access = True
                    enroll.status = Enrollment.STATUS.begin
                    enroll.save()

                    text1 = f'Selamat, Anda sudah mendapatkan akses kelas {enroll.course.title}. '
                    text2 = f'Gabung ke grup chat menggunakan link <a href="{enroll.batch.link_group}">ini</a> untuk mendapatkan informasi lebih lanjut.'
                    notif_msg = text1 + text2 if settings.COURSE_CONFIGS['REQUIRED_LINK_GROUP'] else text1

                    utils.send_notification(
                        enroll.user, f'Akses kelas {enroll.course.title} di berikan', notif_msg)
            
            sweetify.success(request, _(f'Berhasil memberikan akses massal'), button='OK', icon='success')

    context = {
        'menu_active': 'registrants',
        'title': _('Pendaftar Kursus'),
        'registrants': registrants,
        'form': form
    }
    return render(request, 'backoffice/courses/registrants.html', context)


@superuser_required
def ajax_change_status_registrants(request):
    id = request.GET.get('id', None)
    status = request.GET.get('status', None)
    enroll = get_object_or_404(Enrollment, id=id)
    if settings.COURSE_CONFIGS['REQUIRED_LINK_GROUP'] and \
            not enroll.course.batchs.last().link_group:
        data = {
            'status': False,
            'message': f'Link grup pada batch {enroll.batch} belum diisi',
            'batch': enroll.batch.batch
        }
        return JsonResponse(data, status=200)
   
    enroll.allowed_access = status
    enroll.status = Enrollment.STATUS.begin
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


@superuser_required
def bulk_register(request):
    form = FormBulkRegister(request.POST or None, request.FILES or None)
    if form.is_valid():
        csv_buffer = form.sync_users()
        response = HttpResponse(csv_buffer.getvalue(), content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename=reject-data.csv'
        return response

    context = {
        'menu_active': 'registrants',
        'title': 'Registrasi Masal',
        'form': form,
        'title_submit': _("Proses")
    }
    return render(request, 'backoffice/form.html', context)


@superuser_required
def export_data(request, id):
    course = get_object_or_404(
        Courses.objects.prefetch_related(
            Prefetch('modules', queryset=Module.objects.publish()),
            Prefetch('modules__sections', queryset=Section.objects.publish())
        ).select_related('vendor'),
        id=id
    )

    ex_course = ExportCourse(course)
    ex_course.export_data()

    response = HttpResponse(ex_course.zip_buffer.getvalue(),
                            content_type="application/x-zip-compressed")
    response['Content-Disposition'] = 'attachment; filename=%s' % ex_course.zip_filename
    return response


@superuser_required
def import_data(request):
    form = FormImportCourse(data=request.POST or None, files=request.FILES or None)
    if form.is_valid():
        form.import_course()
        sweetify.success(request, _('Berhasil impor data'), button='OK', icon='success')

    context = {
        'menu_active': 'course',
        'title': 'Impor Materi Kursus',
        'form': form,
        'title_submit': _("Proses")
    }
    return render(request, 'backoffice/form.html', context)
