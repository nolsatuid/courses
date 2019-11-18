from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required

from nolsatu_courses.apps.courses.models import Courses


def details(request, slug):
    course = get_object_or_404(Courses, slug=slug)
    context = {
        'title': course.title,
        'course': course
    }
    return render(request, 'website/courses/details.html', context)


@login_required
def user_courses(request):
    enrolls = request.user.enroll.all()
    context = {
        'title': _('Daftar Kursusmu'),
        'courses': [enroll.course for enroll in enrolls]
    }
    return render(request, 'website/index.html', context)
