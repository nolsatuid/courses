from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from nolsatu_courses.apps.courses.models import Module, Section, TaskUploadSettings
from nolsatu_courses.backoffice.sections.forms import FormSection, FormTaskSetting


@staff_member_required
def index(request, id):
    module = get_object_or_404(Module, id=id, course__vendor__users__email=request.user.email)
    context = {
        'menu_active': 'course',
        'title': _('Daftar Bab'),
        'sections': module.sections.all(),
        'module': module,
        'sidebar': True
    }
    return render(request, 'vendors/sections/index.html', context)


@staff_member_required
def create(request, id):
    module = get_object_or_404(Module, id=id, course__vendor__users__email=request.user.email)
    form = FormSection(data=request.POST or None, files=request.FILES or None)
    if form.is_valid():
        section = form.save(commit=False)
        section.module = module
        section.save()
        messages.success(request, _(f"Berhasil tambah bab {section.title}"))
        return redirect('vendors:sections:index', id=id)

    context = {
        'menu_active': 'course',
        'title': _('Tambah Bab'),
        'form': form,
        'title_submit': 'Simpan'
    }

    template = 'vendors/form-editor.html'
    if settings.FEATURE["MARKDOWN_VENDORS_EDITOR"]:
        template = 'vendors/form-editor-markdown.html'

    return render(request, template, context)


@staff_member_required
def edit(request, id):
    section = get_object_or_404(Section, id=id, module__course__vendor__users__email=request.user.email)
    form = FormSection(data=request.POST or None, files=request.FILES or None, instance=section)
    if form.is_valid():
        section = form.save()
        messages.success(request, _(f"Berhasil ubah bab {section.title}"))
        return redirect('vendors:sections:index', id=section.module.id)

    context = {
        'menu_active': 'course',
        'title': _('Ubah Bab'),
        'form': form,
        'title_submit': 'Simpan'
    }

    template = 'vendors/form-editor.html'
    if settings.FEATURE["MARKDOWN_VENDORS_EDITOR"]:
        template = 'vendors/form-editor-markdown.html'

    return render(request, template, context)


@staff_member_required
def delete(request, id):
    section = get_object_or_404(Section, id=id, module__course__vendor__users__email=request.user.email)
    section.delete()
    messages.success(request, 'Berhasil hapus bab')
    return redirect('vendors:sections:index', id=section.module.id)


@staff_member_required
def details(request, id):
    section = get_object_or_404(Section, id=id, module__course__vendor__users__email=request.user.email)

    context = {
        'menu_active': 'course',
        'title': 'Detail Bab',
        'section': section,
        'task_setting': TaskUploadSettings.objects.filter(section=section).first()
    }
    return render(request, 'vendors/sections/detail.html', context)


@staff_member_required
def task_setting(request, id):
    section = get_object_or_404(Section, id=id, module__course__vendor__users__email=request.user.email)
    set_to_task = TaskUploadSettings.objects.filter(section=section).first()
    form = FormTaskSetting(data=request.POST or None, instance=set_to_task or None)
    if form.is_valid():
        set_to_task = form.save(commit=False)
        set_to_task.section = section
        set_to_task.save()
        form.save_m2m()
        messages.success(request, _(f"Berhasil ubah pengaturan tugas"))
        return redirect('vendors:sections:index', id=section.module.id)

    context = {
        'menu_active': 'course',
        'title': _('Pengaturan Tugas'),
        'form': form,
        'title_submit': 'Simpan'
    }

    template = 'vendors/form-editor.html'
    if settings.FEATURE["MARKDOWN_VENDORS_EDITOR"]:
        template = 'vendors/form-editor-markdown.html'

    return render(request, template, context)
