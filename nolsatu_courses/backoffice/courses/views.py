from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required

from nolsatu_courses.apps.courses.models import Courses


@staff_member_required
def index(request):
    context = {
        'title': _('Daftar Kursus')
    }
    return render(request, 'backoffice/courses/index.html', context)
