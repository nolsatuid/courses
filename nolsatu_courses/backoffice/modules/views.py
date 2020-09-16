import sweetify

from django.conf import settings
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404

from nolsatu_courses.apps.courses.models import Courses, Module
from nolsatu_courses.apps.decorators import superuser_required

from .forms import FormModule


@superuser_required
def index(request, id):
    course = get_object_or_404(Courses, id=id)
    context = {
        'menu_active': 'course',
        'title': _('Daftar Modul'),
        'modules': course.modules.all(),
        'course': course,
        'sidebar': True
    }
    return render(request, 'backoffice/modules/index.html', context)


@superuser_required
def add(request, id):
    course = get_object_or_404(Courses, id=id)
    form = FormModule(data=request.POST or None, files=request.FILES or None)
    if form.is_valid():
        module = form.save(commit=False)
        module.course = course
        module.save()
        sweetify.success(request, _(f"Berhasil tambah modul {module.title}"), button='OK', icon='success')
        return redirect('backoffice:modules:index', id=id)

    context = {
        'menu_active': 'course',
        'title': _('Tambah Modul'),
        'form': form,
        'title_submit': 'Simpan'
    }

    template = 'backoffice/form-editor.html'
    if settings.FEATURE["MARKDOWN_BACKOFFICE_EDITOR"]:
        template = 'backoffice/form-editor-markdown.html'

    return render(request, template, context)


@superuser_required
def edit(request, id):
    module = get_object_or_404(Module, id=id)
    form = FormModule(data=request.POST or None, files=request.FILES or None, instance=module)
    if form.is_valid():
        module = form.save()
        sweetify.success(request, _(f"Berhasil ubah modul {module.title}"), button='OK', icon='success')
        return redirect('backoffice:modules:index', id=module.course.id)

    context = {
        'menu_active': 'course',
        'title': _('Ubah Modul'),
        'form': form,
        'title_submit': 'Simpan'
    }

    template = 'backoffice/form-editor.html'
    if settings.FEATURE["MARKDOWN_BACKOFFICE_EDITOR"]:
        template = 'backoffice/form-editor-markdown.html'

    return render(request, template, context)


@superuser_required
def delete(request, id):
    module = get_object_or_404(Module, id=id)
    module.delete()
    sweetify.success(request, 'Berhasil hapus modul', button='OK', icon='success')
    return redirect('backoffice:modules:index', id=module.course.id)


@superuser_required
def details(request, id):
    module = get_object_or_404(Module, id=id)

    context = {
        'menu_active': 'course',
        'title': 'Detail Modul',
        'module': module
    }
    return render(request, 'backoffice/modules/detail.html', context)


@superuser_required
def preview(request, id):
    module = get_object_or_404(Module, id=id)
    download = request.GET.get('download', '')
    if download:
        module_pdf = module.export_to_pdf()
        return module_pdf

    context = {
        'menu_active': 'course',
        'title': 'Preview Ekspor PDF',
        'module': module,
        'section_all': module.sections.publish()
    }
    return render(request, 'backoffice/modules/preview.html', context)
