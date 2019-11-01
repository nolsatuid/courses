from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.courses.models import Courses


def index(request):
    context = {
        'title': _('Kursus'),
        'courses': Courses.objects.all()
    }
    return render(request, 'website/index.html', context)



@login_required
def test_login(request):
    context = {
        'title': _('Kursus'),
        'courses': Courses.objects.all()
    }
    return render(request, 'website/index.html', context)
