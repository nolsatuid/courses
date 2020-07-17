from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404,render, redirect
from nolsatu_courses.apps.courses.models import Courses


@staff_member_required
def get_list_courses(request):
    context = {
        'courses': Courses.objects.filter(vendor__users__email=request.user.email),
        'menu_active': 'course',
        'title': _('Daftar Kursus'),
        'sidebar': True
    }
    return render(request, 'vendors/courses/courses-list.html', context)


@staff_member_required
def get_details_courses(request, courses_id):
    course = get_object_or_404(Courses, id=courses_id, vendor__users__email=request.user.email)
    context = {
        'menu_active': 'course',
        'title': 'Detail Kursus',
        'course': course,
    }
    return render(request, 'vendors/courses/course-detail.html', context)
