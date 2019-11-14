from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.courses.models import Section, Module


def details(request, slug):
    section = get_object_or_404(Section, slug=slug)
    next = Section.objects.filter(order__gt=section.order, module=section.module).first()
    next_type = 'section'
    if not next:
        next = Module.objects.filter(order__gt=section.module.order).first()
        next_type = 'module'
    prev = Section.objects.filter(order__lt=section.order, module=section.module).last()
    prev_type = 'section'
    if not prev:
        prev = Module.objects.filter(id=section.module.id).last()
        prev_type = 'module'

    context = {
        'title': section.title,
        'section': section,
        'prev': prev,
        'next': next,
        'next_type': next_type,
        'prev_type': prev_type 
    }
    return render(request, 'website/sections/details.html', context)
