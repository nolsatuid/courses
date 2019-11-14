from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.courses.models import Section


def details(request, slug):
    section = get_object_or_404(Section, slug=slug)
    context = {
        'title': section.title,
        'section': section
    }
    return render(request, 'website/sections/details.html', context)
