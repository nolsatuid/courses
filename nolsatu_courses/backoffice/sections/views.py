import sweetify

from django.conf import settings
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404

from nolsatu_courses.apps.courses.models import Module, Section, TaskUploadSettings
from nolsatu_courses.apps.decorators import superuser_required
from .forms import FormSection, FormTaskSetting


@superuser_required
def index(request, id):
    module = get_object_or_404(Module, id=id)
    context = {
        'menu_active': 'course',
        'title': _('Daftar Bab'),
        'sections': module.sections.all(),
        'module': module,
        'sidebar': True
    }
    return render(request, 'backoffice/sections/index.html', context)


@superuser_required
def add(request, id):
    module = get_object_or_404(Module, id=id)
    form = FormSection(data=request.POST or None, files=request.FILES or None)
    if form.is_valid():
        section = form.save(commit=False)
        section.module = module
        section.save()
        sweetify.success(request, _(f"Berhasil tambah bab {section.title}"), button='OK', icon='success')
        return redirect('backoffice:sections:index', id=id)

    context = {
        'menu_active': 'course',
        'title': _('Tambah Bab'),
        'form': form,
        'title_submit': 'Simpan'
    }

    template = 'backoffice/form-editor.html'
    if settings.FEATURE["MARKDOWN_BACKOFFICE_EDITOR"]:
        template = 'backoffice/form-editor-markdown.html'

    return render(request, template, context)


@superuser_required
def edit(request, id):
    section = get_object_or_404(Section, id=id)
    form = FormSection(data=request.POST or None, files=request.FILES or None, instance=section)
    if form.is_valid():
        section = form.save()
        sweetify.success(request, _(f"Berhasil ubah bab {section.title}"), button='OK', icon='success')
        return redirect('backoffice:sections:index', id=section.module.id)

    context = {
        'menu_active': 'course',
        'title': _('Ubah Bab'),
        'form': form,
        'title_submit': 'Simpan'
    }

    template = 'backoffice/form-editor.html'
    if settings.FEATURE["MARKDOWN_BACKOFFICE_EDITOR"]:
        template = 'backoffice/form-editor-markdown.html'

    return render(request, template, context)


@superuser_required
def delete(request, id):
    section = get_object_or_404(Section, id=id)
    section.delete()
    sweetify.success(request, 'Berhasil hapus bab', button='OK', icon='success')
    return redirect('backoffice:sections:index', id=section.module.id)


@superuser_required
def details(request, id):
    section = get_object_or_404(Section, id=id)

    context = {
        'menu_active': 'course',
        'title': 'Detail Bab',
        'section': section,
        'task_setting': TaskUploadSettings.objects.filter(section=section).first()
    }
    return render(request, 'backoffice/sections/detail.html', context)


@superuser_required
def task_setting(request, id):
    section = get_object_or_404(Section, id=id)
    task_setting = TaskUploadSettings.objects.filter(section=section).first()
    form = FormTaskSetting(data=request.POST or None, instance=task_setting or None)
    if form.is_valid():
        task_setting = form.save(commit=False)
        task_setting.section = section
        task_setting.save()
        form.save_m2m()
        sweetify.success(request, _(f"Berhasil ubah pengaturan tugas"), button='OK', icon='success')
        return redirect('backoffice:sections:index', id=section.module.id)

    context = {
        'menu_active': 'course',
        'title': _('Pengaturan Tugas'),
        'form': form,
        'title_submit': 'Simpan'
    }

    template = 'backoffice/form-editor.html'
    if settings.FEATURE["MARKDOWN_BACKOFFICE_EDITOR"]:
        template = 'backoffice/form-editor-markdown.html'

    return render(request, template, context)
