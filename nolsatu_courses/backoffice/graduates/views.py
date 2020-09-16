import sweetify

from django.conf import settings
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse

from nolsatu_courses.apps import utils
from nolsatu_courses.apps.courses.models import Enrollment, Batch
from nolsatu_courses.apps.decorators import superuser_required
from nolsatu_courses.apps.utils import call_internal_api
from .forms import FormFilterStudent


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

    data = enroll.get_cert_data()
    response = call_internal_api('post', url=settings.NOLSATU_HOST + '/api/internal/generate-certificate/', data=data)
    if response.status_code == 200:
        enroll.status = Enrollment.STATUS.graduate
        enroll.save()
        utils.send_notification(
            enroll.user, 'Selamat! Anda lulus',
            'Selamat, Anda telah berhasil menyelesaikan persyaratan yang diperlukan untuk mendapatkan ' \
            f'Sertifikasi kelulusan pada kelas {enroll.course.title}. ' \
            'Silahkan cek sertifikat Anda dimenu Sertifikat pada halaman akun.'
        )
        sweetify.success(request, f'Berhasil mengubah status {enroll.user.get_full_name()} menjadi lulusan', button='OK', icon='success')
    else:
        sweetify.error(request, f'Gagal mengubah status {enroll.user.get_full_name()} menjadi lulusan', button='OK', icon='error')

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
    course = request.GET.get('course', None)
    data = {
        'batch': []
    }
    if course:
        batch = Batch.objects.filter(course=course)
        data['batch'] = [
            {
                'id': b.id,
                'batch': b.batch
            } for b in batch
        ]

    return JsonResponse(data, status=200)
