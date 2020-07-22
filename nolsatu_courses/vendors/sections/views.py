from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404

from nolsatu_courses.apps.courses.models import Module, Section, TaskUploadSettings


@staff_member_required
def index(request, id):
    module = get_object_or_404(Module, id=id, course__vendor__users__email=request.user.email)
    context = {
        'menu_active': 'course',
        'title': _('Daftar Bab'),
        'sections': module.sections.all(),
        'module': module,
        'sidebar': True
    }
    return render(request, 'vendors/sections/index.html', context)
