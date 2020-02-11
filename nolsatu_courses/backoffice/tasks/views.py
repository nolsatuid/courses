from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from nolsatu_courses.apps import utils
from nolsatu_courses.apps.courses.models import Section, CollectTask
from .forms import FormFilterTask


@staff_member_required
def index(request):
    tasks = CollectTask.objects.all()
    form = FormFilterTask(request.GET or None)
    if form.is_valid():
        tasks = form.get_data()

    context = {
        'menu_active': 'task',
        'title': _('Pengumpulan Tugas'),
        'tasks': tasks,
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
        section = Section.objects.filter(module__course=course)
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
    task.save()

    utils.post_inbox(request, task.user, f'Perubahan status tugas',
                     f'Status tugas {task.section.title} Anda di ubah menjadi {CollectTask.STATUS[int(task.status)]}')

    data = {}
    return JsonResponse(data, status=200)
