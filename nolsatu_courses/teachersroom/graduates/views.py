from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.courses.models import Enrollment
from nolsatu_courses.apps.decorators import teacher_required
from .forms import TrainerFormFilterStudent


@teacher_required
def candidate(request):
    candidates = []
    form = TrainerFormFilterStudent(request.GET or None, user_email=request.user.email)

    if form.is_valid():
        students = form.get_data(status=Enrollment.STATUS.finish)
        candidates = [
            {
                'enroll': student,
                'task': student.get_count_task_status()
            } for student in students
        ]

    context = {
        'menu_active': 'graduate',
        'title': _('Kandidat'),
        'candidate': candidates,
        'form': form
    }
    return render(request, 'teachersroom/graduates/candidate.html', context)


@teacher_required
def index(request):
    graduates = []
    form = TrainerFormFilterStudent(request.GET or None, user_email=request.user.email)

    if form.is_valid():
        graduates = form.get_data(status=Enrollment.STATUS.graduate)

    context = {
        'menu_active': 'graduate',
        'title': _('Lulusan'),
        'graduates': graduates,
        'form': form
    }
    return render(request, 'teachersroom/graduates/index.html', context)
