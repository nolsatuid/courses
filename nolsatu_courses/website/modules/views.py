from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.courses.models import Module, Section


def details(request, slug):
    module = get_object_or_404(Module, slug=slug)
    next = Section.objects.filter(module=module).first()
    next_type = 'section'
    if not next:
        next = Module.objects.filter(order__gt=module.order).exclude(id=module.id).first()
        next_type = 'module'
    prev_module = Module.objects.filter(order__lt=module.order).exclude(id=module.id).last()
    prev = Section.objects.filter(module=prev_module).last()
    prev_type = 'section'
    if not prev:
        prev = prev_module
        prev_type = 'module'

    context = {
        'title': module.title,
        'module': module,
        'prev': prev,
        'next': next,
        'next_type': next_type,
        'prev_type': prev_type 
    }
    return render(request, 'website/modules/details.html', context)
