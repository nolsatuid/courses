from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.courses.models import CollectTask, Courses, Batch
from nolsatu_courses.apps.decorators import teacher_required
from nolsatu_courses.teachersroom.tasks.forms import TrainerFormFilterTask, TrainerFormFilterTaskReport


@teacher_required
def index(request):
    tasks = None
    course = None
    form = TrainerFormFilterTask(request.GET or None, user_email=request.user.email)

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
    return render(request, 'teachersroom/tasks/index.html', context)


@teacher_required
def report_index(request):
    users = None
    course = None
    avg_score = None
    batch = None
    form = TrainerFormFilterTaskReport(request.GET or None, user_email=request.user.email)

    if form.is_valid():
        users, avg_score, batch = form.get_data()

        if users:
            course = form.cleaned_data['course']

    context = {
        'menu_active': 'task',
        'title': _('Pelaporan Tugas'),
        'users': users,
        'course': course,
        'avg_score': avg_score,
        'form': form,
        'batch': batch
    }
    return render(request, 'teachersroom/tasks/report_index.html', context)


@teacher_required
def report_detail(request, user_id, course_id, batch_id):
    user = get_object_or_404(User, id=user_id)
    course = get_object_or_404(Courses, id=course_id, enrolled__user__in=[user])

    # check user in batch related with teachers
    get_object_or_404(Batch, id=batch_id, enrollments__user=user, teaches__user__email=request.user.email)

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
    return render(request, 'teachersroom/tasks/report_detail.html', context)
