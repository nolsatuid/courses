from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from .forms import FormFilterVendor


@staff_member_required
def index(request):
    template_name = 'vendors/dashboard.html'
    statistics = None
    quiz_stats = None
    batch = None
    form = FormFilterVendor(request.GET or None, user_email=request.user.email)
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
    return render(request, template_name, context)
