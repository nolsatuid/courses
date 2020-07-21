from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404

from nolsatu_courses.apps.courses.models import Courses, Module


@staff_member_required
def index(request, id):
    course = get_object_or_404(Courses, id=id, vendor__users__email=request.user.email)
    context = {
        'menu_active': 'course',
        'title': _('Daftar Modul'),
        'modules': course.modules.all(),
        'course': course,
        'sidebar': True
    }
    return render(request, 'vendors/modules/index.html', context)
