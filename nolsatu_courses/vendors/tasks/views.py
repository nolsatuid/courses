from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import localtime

from nolsatu_courses.apps import utils
from nolsatu_courses.apps.courses.models import Section, CollectTask, Batch, Courses
from .forms import FormFilterTaskVendor


@staff_member_required
def index(request):
    tasks = CollectTask.objects.filter(
            section__module__course__vendor__users__email=request.user.email
        )
    form = FormFilterTaskVendor(request.GET or None, user_email=request.user.email)
    if form.is_valid():
        tasks = form.get_data()

    context = {
        'menu_active': 'task',
        'title': _('Pengumpulan Tugas'),
        'tasks': tasks,
        'form': form
    }
    return render(request, 'vendors/tasks/index.html', context)


@staff_member_required
def ajax_change_status(request):
    id = request.GET.get('task_id', None)
    status_id = request.GET.get('status_id', None)
    task = get_object_or_404(CollectTask, id=id, section__module__course__vendor__users__email=request.user.email)
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
