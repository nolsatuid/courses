import sweetify

from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import Http404

from nolsatu_courses.apps.accounts.models import MemberNolsatu
from nolsatu_courses.apps.courses.models import Module, Section
from nolsatu_courses.apps.decorators import enroll_required
from nolsatu_courses.apps.utils import check_on_activity


@login_required
@enroll_required
def details(request, slug):
    module = get_object_or_404(
        Module.objects.select_related("course"), slug=slug
    )

    first_module = module.course.get_first_module()
    if not module.id == first_module.id:
        # cek apakah module ini sudah pernah dilihat, jika belum maka
        # maka cek id module apakah sama dengan next_page_slug, jika tidak sama
        # maka munculkan halaman 404
        if not check_on_activity(slug=module.slug, type_field='module'):
            if module.slug != request.session.get('next_page_slug'):
                raise Http404()

    pagination = get_pagination(request, module, set_session=True)
    prev_type = pagination['prev_type']
    prev = pagination['prev']
    next_slug = pagination['next']

    # handle ketika user belum mengumpulkan tugas pada sesi sebelumnya
    # jika page_type adalah section dan section memiliki tugas
    if prev_type == 'section' and prev.is_task:
        if not request.user.collect_tasks.filter(section=prev):
            sweetify.warning(
                request, _(f"Kamu harus mengumpulkan tugas pada sesi {prev.title}"),
                button='OK', icon='warning', timer=10000
            )
            return redirect("website:sections:details", prev.slug)

    # jika next kosong berarti berada pada sesi terakhir
    is_complete_tasks = None
    course_finish_slug = ""
    if not next_slug:
        is_complete_tasks = module.course.is_complete_tasks(request.user)
        course_finish_slug = module.course.slug

    module_all = module.course.modules.publish().prefetch_related(
        Prefetch('sections', queryset=Section.objects.publish())
    )

    context = {
        'title': module.title,
        'module': module,
        'pagination': pagination,
        'module_all': module_all,
        'is_complete_tasks': is_complete_tasks,
        "course_finish_slug": course_finish_slug
    }

    # save activities user to module
    if module.has_enrolled(request.user):
        module.get_or_create_activity(user=request.user, course=module.course)
        module.delete_cache(request.user)

    return render(request, 'website/modules/details.html', context)


def preview(request, slug):
    is_auth = request.user.is_authenticated
    is_superuser = request.user.is_superuser
    is_trainer = is_auth and request.user.nolsatu.role == MemberNolsatu.ROLE.trainer

    if is_superuser or is_trainer:
        module = get_object_or_404(Module, slug=slug)
        pagination = get_pagination(request, module)
    else:
        module = get_object_or_404(Module, slug=slug, is_visible=True)
        pagination = None

    trainer_have_course = is_trainer and request.user.teaches.filter(batch__course=module.course).exists()
    if is_trainer and not trainer_have_course:
        raise Http404()

    is_show_all_materi = is_superuser or trainer_have_course

    module_all = module.course.modules.publish().prefetch_related(
        Prefetch('sections', queryset=Section.objects.publish())
    )

    context = {
        'title': module.title,
        'module': module,
        'pagination': pagination,
        'module_all': module_all,
        'is_show_all_materi': is_show_all_materi
    }
    return render(request, 'website/modules/preview.html', context)


def get_pagination(request, module, set_session=False):
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

    # set session
    if set_session:
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
