from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from nolsatu_courses.apps.decorators import teacher_required
from .forms import FormFilter


@teacher_required
def index(request):
    statistics = None
    quiz_stats = None
    batch = None
    form = FormFilter(request.GET or None)
    if form.is_valid():
        data = form.get_data()
        course = form.cleaned_data['course']
        batch = form.cleaned_data['batch'].id
        statistics = {
            'total_registrant': len(data),
            'course': course,
            'data': data,
            'global_progress': form.global_progress()
        }
        quiz_stats = form.get_quiz_stats()

    context = {
        'menu_active': 'dashboard',
        'title': _('Dashboard'),
        'statistics': statistics,
        'form': form,
        'quiz_stats': quiz_stats,
        'batch': batch
    }
    return render(request, 'teachersroom/index.html', context)
