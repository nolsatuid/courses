from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.courses.models import Module


def details(request, slug):
    module = get_object_or_404(Module, slug=slug)
    context = {
        'title': module.title,
        'module': module
    }
    return render(request, 'website/modules/details.html', context)
