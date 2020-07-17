from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
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
