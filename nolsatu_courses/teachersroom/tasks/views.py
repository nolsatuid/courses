from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.decorators import teacher_required
from nolsatu_courses.teachersroom.tasks.forms import TrainerFormFilterTask


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