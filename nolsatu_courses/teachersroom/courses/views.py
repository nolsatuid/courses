from nolsatu_courses.apps.decorators import teacher_required
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from nolsatu_courses.apps.courses.models import Teach


@teacher_required
def index(request):
    teaches = Teach.objects.select_related('batch__course')\
        .order_by('batch')\
        .filter(user=request.user)
    context = {
        'title': _('Kursus Anda'),
        'teaches': teaches
    }
    return render(request, 'teachersroom/courses/index.html', context)
