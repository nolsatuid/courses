from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from .forms import FormFilter


@staff_member_required
def index(request):
    statistics = None

    form = FormFilter(request.GET or None)
    if form.is_valid():
        data = form.get_data()
        course = form.cleaned_data['course']
        statistics = {
            'total_registrant': len(data),
            'course': course,
            'data': data,
            'global_progress': form.global_progress()
        }

    context = {
        'menu_active': 'dashboard',
        'title': _('Dashboard'),
        'statistics': statistics,
        'form': form,
    }
    return render(request, 'backoffice/index.html', context)
