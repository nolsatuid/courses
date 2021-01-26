from django.db.models.expressions import Subquery
from nolsatu_courses.apps.decorators import teacher_required
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from nolsatu_courses.apps.courses.models import Batch, Courses, Teach


@teacher_required
def index(request):
    courses = Courses.objects.filter(
        pk__in=Subquery(
            Batch.objects.values_list('course', flat=True)
                .filter(
                    pk__in=Subquery(
                        Teach.objects.filter(user=request.user)
                        .values_list('batch', flat=True)
                    )
                ).distinct()
        )
    )
    batchs = Batch.objects.filter(teaches__user=request.user)

    context = {
        'title': _('Kursus Anda'),
        'courses': courses,
        'batchs': batchs
    }
    return render(request, 'teachersroom/courses/index.html', context)
