from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Avg, F
from django.db.models.functions import Concat
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import localtime

from nolsatu_courses.apps import utils
from nolsatu_courses.apps.courses.models import Section, CollectTask, Batch, Courses, Enrollment
from .forms import FormFilterTaskVendor, FormFilterTaskReportVendor


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


@staff_member_required
def report_index(request):
    user_report_task = CollectTask.objects.filter(
        section__module__course__vendor__users__email=request.user.email
    ).values("section__module__course").annotate(user_id=F("user__id"), course_id=F("section__module__course__id"),
                                                 name=Concat('user__first_name', 'user__last_name'),
                                                 username=F("user__username"), avg_score=Avg("score"),
                                                 title=F("section__module__course__title"))
    download = request.GET.get('download', '')
    form = FormFilterTaskReportVendor(request.GET or None, user_email=request.user.email)
    if form.is_valid():
        user_report_task = form.get_data()

        if download:
            batch = form.cleaned_data['batch']
            csv_buffer = form.download_report()
            response = HttpResponse(csv_buffer.getvalue(), content_type="text/csv")
            response['Content-Disposition'] = f'attachment; filename=Tugas-Angkatan-{batch}.csv'
            return response

    context = {
        'menu_active': 'task',
        'title': _('Pelaporan Tugas'),
        'users': user_report_task,
        'form': form
    }
    return render(request, 'vendors/tasks/report_index.html', context)


@staff_member_required
def report_detail(request, user_id, course_id):
    user = get_object_or_404(User, id=user_id)
    course = get_object_or_404(Courses, id=course_id, enrolled__user__in=[user],
                               vendor__users__email=request.user.email)
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
    return render(request, 'vendors/tasks/report_detail.html', context)
