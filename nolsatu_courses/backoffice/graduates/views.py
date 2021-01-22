import sweetify

from django.conf import settings
from django.db import transaction, DatabaseError
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse

from nolsatu_courses.apps import utils
from nolsatu_courses.apps.courses.models import Enrollment, Batch
from nolsatu_courses.apps.decorators import superuser_required
from nolsatu_courses.apps.utils import call_internal_api
from .forms import FormFilterStudent
from ...apps.accounts.models import MemberNolsatu


@superuser_required
def index(request):
    graduates = []
    form = FormFilterStudent(request.GET or None)
    if form.is_valid():
        graduates = form.get_data(status=Enrollment.STATUS.graduate)

    context = {
        'menu_active': 'graduate',
        'title': _('Lulusan'),
        'graduates': graduates,
        'form': form
    }
    return render(request, 'backoffice/graduates/index.html', context)


@superuser_required
def candidate(request):
    candidate = []
    form = FormFilterStudent(request.GET or None)
    if form.is_valid():
        students = form.get_data(status=Enrollment.STATUS.finish)
        candidate = [
            {
                'enroll': student,
                'task': student.get_count_task_status()
            } for student in students
        ]

    context = {
        'menu_active': 'graduate',
        'title': _('Kandidat'),
        'candidate': candidate,
        'form': form
    }
    return render(request, 'backoffice/graduates/candidate.html', context)


@superuser_required
def candidate_to_graduate(request, id):
    enroll = get_object_or_404(Enrollment, id=id)
    enroll.note = request.GET.get('note', "")
    enroll.final_score = request.GET.get('final_score', 0)
    enroll.status = Enrollment.STATUS.graduate

    msg = ('Selamat, Anda telah berhasil menyelesaikan persyaratan yang diperlukan untuk mendapatkan '
           f'Sertifikasi kelulusan pada kelas {enroll.course.title}. ')

    if request.GET.get('print_certificate'):
        data = enroll.get_cert_data()
        response = call_internal_api('post', url=settings.NOLSATU_HOST + '/api/internal/generate-certificate/',
                                     data=data)
        if response.status_code == 200:
            msg = ('Selamat, Anda telah berhasil menyelesaikan persyaratan yang diperlukan untuk mendapatkan '
                   f'Sertifikasi kelulusan pada kelas {enroll.course.title}. '
                   'Silahkan cek sertifikat Anda dimenu Sertifikat pada halaman akun.')
        else:
            sweetify.error(request, f'Gagal cetak sertifikat milik {enroll.user.get_full_name()}', button='OK',
                           icon='error')

    try:
        with transaction.atomic():
            enroll.save()
    except DatabaseError:
        return redirect('backoffice:graduates:candidate')

    utils.send_notification(enroll.user, 'Selamat! Anda lulus', msg)

    sweetify.success(request, f'Berhasil mengubah status {enroll.user.get_full_name()} menjadi lulusan',
                     button='OK', icon='success')

    if request.is_ajax():
        data = {
            'message': _("Berhasil set lulus")
        }
        return JsonResponse(data, status=200)

    return redirect('backoffice:graduates:candidate')


@superuser_required
def regenerate_certificate(request, user_id):
    response = call_internal_api('get', url=settings.NOLSATU_HOST + f'/api/internal/regenerate-certificate/{user_id}')
    if response.status_code == 200:
        sweetify.success(request, 'Berhasil perbarui sertifikat', button='OK', icon='success')
    else:
        sweetify.error(request, 'Gagal perbarui sertifikat', button='OK', icon='error')

    return redirect('backoffice:graduates:index')


@superuser_required
def ajax_filter_batch(request):
    """ a view ajax filter used to filtering batch by course
    ...
    Ajax Filter batch by condition user role
    ----------------------------------------
        - backoffice: all batch
        - vendor: batch in course filter by vendor
        - trainer: batch have assigned to teachers
    """

    course = request.GET.get('course', None)

    data = {
        'batch': []
    }

    if course:
        if request.user.nolsatu.role == MemberNolsatu.ROLE.vendor:
            batch = Batch.objects.filter(course=course, course__vendor__user__email=request.user.email)
        elif request.user.nolsatu.role == MemberNolsatu.ROLE.trainer:
            batch = Batch.objects.filter(course=course, teaches__user__email=request.user.email)
        else:
            batch = Batch.objects.filter(course=course)

        data['batch'] = [
            {
                'id': b.id,
                'batch': b.batch
            } for b in batch
        ]

    return JsonResponse(data, status=200)
