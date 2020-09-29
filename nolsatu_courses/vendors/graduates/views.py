import sweetify

from django.conf import settings
from django.db import transaction, DatabaseError
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.courses.models import Enrollment, Batch
from nolsatu_courses.apps.decorators import vendor_member_required
from nolsatu_courses.apps import utils
from .forms import FormFilterStudentVendor


@vendor_member_required
def candidate(request):
    candidate_list = []
    form = FormFilterStudentVendor(request.GET or None, user_email=request.user.email)
    if form.is_valid():
        students = form.get_data(status=Enrollment.STATUS.finish)
        candidate_list = [
            {
                'enroll': student,
                'task': student.get_count_task_status()
            } for student in students
        ]

    context = {
        'menu_active': 'graduate',
        'title': _('Kandidat'),
        'candidate': candidate_list,
        'form': form
    }
    return render(request, 'vendors/graduates/candidate.html', context)


@vendor_member_required
def candidate_to_graduate(request, candidate_id):
    enroll = get_object_or_404(Enrollment, id=candidate_id,
                               course__vendor__users__email=request.user.email)
    enroll.note = request.GET.get('note', "")
    enroll.final_score = request.GET.get('final_score', 0)
    enroll.status = Enrollment.STATUS.graduate

    msg = ('Selamat, Anda telah berhasil menyelesaikan persyaratan yang diperlukan untuk mendapatkan '
           f'Sertifikasi kelulusan pada kelas {enroll.course.title}. ')

    if request.GET.get('print_certificate'):
        data = enroll.get_cert_data()
        response = utils.call_internal_api('post', url=settings.NOLSATU_HOST + '/api/internal/generate-certificate/',
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
    return redirect('vendors:graduates:candidate')


@vendor_member_required
def graduate(request):
    graduates = []
    form = FormFilterStudentVendor(request.GET or None, user_email=request.user.email)
    if form.is_valid():
        graduates = form.get_data(status=Enrollment.STATUS.graduate)

    context = {
        'menu_active': 'graduate',
        'title': _('Lulusan'),
        'graduates': graduates,
        'form': form
    }
    return render(request, 'vendors/graduates/index.html', context)