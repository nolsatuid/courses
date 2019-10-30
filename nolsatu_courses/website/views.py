from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.courses.models import Courses


def index(request):
    context = {
        'title': _('Kursus'),
        'courses': Courses.objects.all()
    }
    return render(request, 'website/index.html', context)
