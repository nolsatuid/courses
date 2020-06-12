from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Prefetch

from nolsatu_courses.apps.courses.models import Module, Section
from nolsatu_courses.apps.decorators import enroll_required


@login_required
@enroll_required
def details(request, slug):
    module = get_object_or_404(
        Module.objects.select_related("course"), slug=slug
    )
    pagination = get_pagination(request, module)
    prev_type = pagination['prev_type']
    prev = pagination['prev']

    # handle ketika user belum mengumpulkan tugas pada sesi sebelumnya
    # jika page_type adalah section dan section memiliki tugas
    if prev_type == 'section' and prev.is_task:
        if not prev.collect_task.all():
            messages.warning(
                request, _(f"Kamu harus mengumpulkan tugas pada sesi {prev.title}")
            )
            return redirect("website:sections:details", prev.slug)

    module_all = module.course.modules.publish().prefetch_related(
        Prefetch('sections', queryset=Section.objects.publish())
    )

    context = {
        'title': module.title,
        'module': module,
        'pagination': pagination,
        'module_all': module_all
    }

    # save activities user to module
    if module.has_enrolled(request.user):
        module.activities_module.update_or_create(
            user=request.user, course=module.course)
        module.delete_cache()

    return render(request, 'website/modules/details.html', context)


def preview(request, slug):
    if request.user.is_superuser:
        module = get_object_or_404(Module, slug=slug)
    else:
        module = get_object_or_404(Module, slug=slug, is_visible=True)

    if request.user.is_superuser:
        pagination = get_pagination(request, module)
    else:
        pagination = None

    module_all = module.course.modules.publish().prefetch_related(
        Prefetch('sections', queryset=Section.objects.publish())
    )

    context = {
        'title': module.title,
        'module': module,
        'pagination': pagination,
        'module_all': module_all
    }
    return render(request, 'website/modules/preview.html', context)


def get_pagination(request, module):
    """
    fungsi untuk mendapatkan pagination
    """
    slugs = module.course.modules.values_list('slug', flat=True)
    next_slug = module.sections.publish().first()
    next_type = "section"
    if not next_slug:
        next_slug = module.get_next(slugs)
        next_type = "module"

    prev_slug = module.get_prev(slugs)
    prev_type = "module"
    if prev_slug:
        if prev_slug.sections.publish().last():
            prev_slug = prev_slug.sections.publish().last()
            prev_type = "section"

    return {
        'prev': prev_slug,
        'next': next_slug,
        'next_type': next_type,
        'prev_type': prev_type
    }
