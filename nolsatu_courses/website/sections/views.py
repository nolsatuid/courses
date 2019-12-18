from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from django.contrib.auth.decorators import login_required

from nolsatu_courses.apps.decorators import enroll_required
from nolsatu_courses.apps.courses.models import (
    Section, Module, CollectTask
)

from .forms import FormUploadFile


@login_required
@enroll_required
def details(request, slug):
    section = get_object_or_404(Section, slug=slug)
    collect_task = section.collect_task.filter(user=request.user).first()
    form = FormUploadFile(
        data=request.POST or None,
        files=request.FILES, section=section,
        user=request.user,
        instance=None if not collect_task else collect_task.file
    )
    if form.is_valid():
        form.save(collect_task=collect_task)
        messages.success(request, _(f"Berhasil mengupload tugas"))
        return redirect('website:sections:details', slug)

    section_slugs = section.module.sections.values_list('slug', flat=True)
    next_slug = section.get_next(section_slugs)
    next_type = 'section'
    if not next_slug:
        module_slugs = section.module.course.modules.values_list('slug', flat=True)
        next_slug = section.module.get_next(module_slugs)
        next_type = 'module'

    prev_slug = section.get_prev(section_slugs)
    prev_type = 'section'
    if not prev_slug:
        prev_slug = section.module
        prev_type = 'module'

    # save activities user to section
    if section.has_enrolled(request.user):
        section.activities_section.get_or_create(user=request.user)

    pagination = {
        'prev': prev_slug,
        'next': next_slug,
        'next_type': next_type,
        'prev_type': prev_type
    }
    context = {
        'title': section.title,
        'section': section,
        'pagination': pagination,
        'form': form,
    }
    return render(request, 'website/sections/details.html', context)


def preview(request, slug):
    section = get_object_or_404(Section, slug=slug)

    context = {
        'title': section.title,
        'section': section,
        'pagination': None
    }
    return render(request, 'website/sections/preview.html', context)
