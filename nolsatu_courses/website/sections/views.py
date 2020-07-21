from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.db.models import Prefetch
from django.http import Http404
from django.contrib.auth.decorators import login_required

from nolsatu_courses.apps.decorators import enroll_required
from nolsatu_courses.apps.courses.models import Section
from nolsatu_courses.apps.utils import check_on_activity

from .forms import FormUploadFile


@login_required
@enroll_required
def details(request, slug):
    section = get_object_or_404(
        Section.objects.select_related("module", "task_setting", "module__course"), slug=slug
    )
    file_not_found = None

    # cek apakah section ini sudah pernah dilihat, jika belum maka
    # maka cek id section apakah sama dengan next_page_slug, jika tidak sama
    # maka munculkan halaman 404
    if not check_on_activity(slug=section.slug, type_field='section'):
        if section.slug != request.session.get('next_page_slug'):
            raise Http404()

    # dapatkan pagination
    pagination = get_pagination(request, section)
    prev_type = pagination['prev_type']
    prev = pagination['prev']
    next_slug = pagination['next']

    # handle ketika user belum mengumpulkan tugas pada sesi sebelumnya
    # jika page_type adalah section dan section memiliki tugas
    if prev_type == 'section' and prev.is_task:
        if not request.user.collect_tasks.filter(section=prev):
            messages.warning(
                request, _(f"Kamu harus mengumpulkan tugas pada sesi {prev.title}")
            )
            return redirect("website:sections:details", prev.slug)

    # form untuk pengumpulan tugas
    collect_task = section.collect_task.filter(user=request.user) \
        .select_related("file").first()

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

    # jika next kosong berarti berada pada sesi terakhir
    is_complete_tasks = None
    if not next_slug:
        is_complete_tasks = section.module.course.is_complete_tasks(request.user)

    module_all = section.module.course.modules.publish().prefetch_related(
        Prefetch('sections', queryset=Section.objects.publish()),
        'activities_module'
    )

    context = {
        'title': section.title,
        'section': section,
        'pagination': pagination,
        'form': form,
        'task': collect_task,
        'is_complete_tasks': is_complete_tasks,
        'file_not_found': file_not_found,
        'module_all': module_all
    }

    # save activities user to section
    if section.has_enrolled(request.user):
        section.activities_section.get_or_create(
            user=request.user, course=section.module.course)
        section.delete_cache(request.user)

    return render(request, 'website/sections/details.html', context)


def preview(request, slug):
    if request.user.is_superuser:
        section = get_object_or_404(Section, slug=slug)
        pagination = get_pagination(request, section)
    else:
        section = get_object_or_404(Section, slug=slug, is_visible=True)
        pagination = None

    module_all = section.module.course.modules.publish().prefetch_related(
        Prefetch('sections', queryset=Section.objects.publish())
    )

    context = {
        'title': section.title,
        'section': section,
        'pagination': pagination,
        'form': FormUploadFile(None, user=request.user),
        'module_all': module_all
    }
    return render(request, 'website/sections/preview.html', context)


def get_pagination(request, section):
    """fungsi untuk mendapatkan pagination
    """
    section_slugs = section.module.sections.publish().values_list('slug', flat=True)
    next_slug = section.get_next(section_slugs)
    next_type = 'section'
    if not next_slug:
        module_slugs = section.module.course.modules.publish().values_list('slug', flat=True)
        next_slug = section.module.get_next(module_slugs)
        next_type = 'module'

    prev_slug = section.get_prev(section_slugs)
    prev_type = 'section'
    if not prev_slug:
        prev_slug = section.module
        prev_type = 'module'

    # set session
    request.session['next_type'] = next_type
    request.session['next_page_slug'] = next_slug.slug if next_slug else None
    request.session['prev_type'] = prev_type
    request.session['prev_page_slug'] = prev_slug.slug if prev_slug else None

    return {
        'prev': prev_slug,
        'next': next_slug,
        'next_type': next_type,
        'prev_type': prev_type
    }
