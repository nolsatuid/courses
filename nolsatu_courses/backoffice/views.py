from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from .forms import FormFilter


@staff_member_required
def index(request):
    statistic = None
    form = FormFilter(request.GET or None)
    if form.is_valid():
        statistic = form.get_data()

    context = {
        'menu_active': 'dashboard',
        'title': _('Dashboard'),
        'statistic': statistic,
        'form': form,
    }
    return render(request, 'backoffice/index.html', context)
