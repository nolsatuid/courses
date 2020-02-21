from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages

from nolsatu_courses.apps.courses.models import Enrollment, Batch
from .forms import FormFilterStudent


@staff_member_required
def index(request):
    graduates = Enrollment.objects.filter(status=Enrollment.STATUS.graduate)
    form = FormFilterStudent(request.GET or None)
    if form.is_valid():
        graduates = form.get_data(students=graduates)

    context = {
        'menu_active': 'graduate',
        'title': _('Lulusan'),
        'graduates': graduates,
        'form': form
    }
    return render(request, 'backoffice/graduates/index.html', context)


@staff_member_required
def candidate(request):
    students = Enrollment.objects.filter(status = Enrollment.STATUS.finish)
    form = FormFilterStudent(request.GET or None)
    if form.is_valid():
        students = form.get_data(students=students)

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


@staff_member_required
def candidate_to_graduate(request, id):
    enroll = get_object_or_404(Enrollment, id=id)
    enroll.status = Enrollment.STATUS.graduate
    enroll.save()
    messages.success(request, f'Berhasil mengubah status {enroll.user.username} menjadi lulusan')
    return redirect('backoffice:graduates:candidate')


@staff_member_required
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
