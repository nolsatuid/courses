from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from django.contrib.auth.decorators import login_required

from nolsatu_courses.apps.decorators import enroll_required, course_was_started
from nolsatu_courses.apps.courses.models import Section

from .forms import FormUploadFile


@login_required
@enroll_required
@course_was_started
def details(request, slug):
    section = get_object_or_404(Section, slug=slug)
    file_not_found = None

    # form untuk pengumpulan tugas
    collect_task = section.collect_task.filter(user=request.user).first()

    # jika ada file
    if hasattr(collect_task, 'file'):
        # cek apakah objek file bisa mengambil file pada direktorinya
        try:
            collect_task.file.file.file
            file_not_found = False
        except (FileNotFoundError, AttributeError):
            # jika tidak bisa, kosongkan field file
            collect_task.file = None
            collect_task.save(update_fields=['file'])
            file_not_found = True

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

    # dapatkan pagination
    pagination = get_pagination(request, section)
    prev_type = pagination['prev_type']
    prev = pagination['prev']
    next_slug = pagination['next']

    # jika next kosong berarti berada pada sesi terakhir
    is_complete_tasks = None
    if not next_slug:
        is_complete_tasks = section.module.course.is_complete_tasks(request.user)

    # handle ketika user belum mengumpulkan tugas pada sesi sebelumnya
    # jika page_type adalah section dan section memiliki tugas
    if prev_type == 'section' and prev.is_task:
        if not prev.collect_task.all():
            messages.warning(
                request, _(f"Kamu harus mengumpulkan tugas pada sesi {prev.title}")
            )
            return redirect("website:sections:details", prev.slug)

    context = {
        'title': section.title,
        'section': section,
        'pagination': pagination,
        'form': form,
        'task': collect_task,
        'is_complete_tasks': is_complete_tasks,
        'file_not_found': file_not_found
    }

    # save activities user to section
    if section.has_enrolled(request.user):
        section.activities_section.get_or_create(
            user=request.user, course=section.module.course)

    return render(request, 'website/sections/details.html', context)


def preview(request, slug):
    if request.user.is_superuser:
        section = get_object_or_404(Section, slug=slug)
        pagination = get_pagination(request, section)
    else:
        section = get_object_or_404(Section, slug=slug, is_visible=True)
        pagination = None

    context = {
        'title': section.title,
        'section': section,
        'pagination': pagination,
        'form': FormUploadFile(None, user=request.user)
    }
    return render(request, 'website/sections/preview.html', context)


def get_pagination(request, section):
    """fungsi untuk mendapatkan pagination
    """
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

    return {
        'prev': prev_slug,
        'next': next_slug,
        'next_type': next_type,
        'prev_type': prev_type
    }
