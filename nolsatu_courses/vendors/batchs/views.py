from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required

from nolsatu_courses.apps.courses.models import Batch


@staff_member_required
def index(request):
    context = {
        'menu_active': 'batch',
        'title': _('Daftar Angkatan'),
        'batchs': Batch.objects.select_related('course'),
        'sidebar': True
    }
    return render(request, 'vendors/batchs/index.html', context)
