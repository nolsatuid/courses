from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.courses.models import Module, Section, Activity


def details(request, slug):
    module = get_object_or_404(Module, slug=slug)
    slugs = Module.objects.values_list('slug', flat=True)
    next_slug = module.sections.first()
    next_type = "section"
    if not next_slug:
        next_slug = module.get_next(slugs)
        next_type = "module"

    prev_slug = module.get_prev(slugs)
    prev_type = "module"
    if prev_slug:
        if prev_slug.sections.last():
            prev_slug = prev_slug.sections.last()
            prev_type = "section"

    # save activities user to module
    if module.has_enrolled(request.user):
        module.activities_module.get_or_create(user=request.user)

    pagination = {
        'prev': prev_slug,
        'next': next_slug,
        'next_type': next_type,
        'prev_type': prev_type
    }
    context = {
        'title': module.title,
        'module': module,
        'pagination': pagination
    }
    return render(request, 'website/modules/details.html', context)
