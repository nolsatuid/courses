from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import localtime

from nolsatu_courses.apps import utils
from nolsatu_courses.apps.courses.models import Section, CollectTask, Batch, Courses
from .forms import FormFilterTask, FormFilterTaskReport


@staff_member_required
def index(request):
    tasks = None
    course = None
    form = FormFilterTask(request.GET or None)
    if form.is_valid():
        tasks = form.get_data()
    if tasks:
        course = tasks.first().section.module.course.title

    context = {
        'menu_active': 'task',
        'title': _('Pengumpulan Tugas'),
        'tasks': tasks,
        'course': course,
        'form': form
    }
    return render(request, 'backoffice/tasks/index.html', context)


@staff_member_required
def ajax_filter_section(request):
    course = request.GET.get('course', None)
    data = {
        'section': []
    }
    if course:
        section = Section.objects.filter(module__course=course, is_task=True)
        data['section'] = [
            {
                'id': s.id,
                'name': s.title
            } for s in section
        ]

    return JsonResponse(data, status=200)


@staff_member_required
def ajax_change_status(request):
    id = request.GET.get('task_id', None)
    status_id = request.GET.get('status_id', None)
    task = get_object_or_404(CollectTask, id=id)
    task.status = status_id
    task.note = request.GET.get('note', None)
    task.score = request.GET.get('score', 0)
    task.save()

    utils.send_notification(
        task.user,
        f'Perubahan status tugas',
        f'Status tugas {task.section.title} Anda di ubah menjadi {CollectTask.STATUS[int(task.status)]}'
    )

    data = {
        'update_at': localtime(task.update_at).strftime("%d %B %Y, %H:%M")
    }
    return JsonResponse(data, status=200)


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
                'name': b.batch
            } for b in batch
        ]

    return JsonResponse(data, status=200)


@staff_member_required
def report_index(request):
    users = None
    course = None
    avg_score = None
    download = request.GET.get('download', '')
    form = FormFilterTaskReport(request.GET or None)
    if form.is_valid():
        users, avg_score = form.get_data()

        if download:
            batch = form.cleaned_data['batch']
            csv_buffer = form.download_report()
            response = HttpResponse(csv_buffer.getvalue(), content_type="text/csv")
            response['Content-Disposition'] = f'attachment; filename=Tugas-Angkatan-{batch}.csv'
            return response

        if users:
            course = form.cleaned_data['course']

    context = {
        'menu_active': 'task',
        'title': _('Pelaporan Tugas'),
        'users': users,
        'course': course,
        'avg_score': avg_score,
        'form': form
    }
    return render(request, 'backoffice/tasks/report_index.html', context)


@staff_member_required
def report_detail(request, user_id, course_id):
    user = get_object_or_404(User, id=user_id)
    course = get_object_or_404(Courses, id=course_id, enrolled__user__in=[user])
    modules = course.modules.order_by('order')
    tasks = CollectTask.objects.filter(section__module__course=course, user=user)
    tasks = {
        t.section.id: t.score
        for t in tasks
    }
    context = {
        'menu_active': 'task',
        'title': _('Pelaporan Tugas'),
        'user': user,
        'course': course,
        'modules': modules,
        'tasks': tasks
    }
    return render(request, 'backoffice/tasks/report_detail.html', context)
