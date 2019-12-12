from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import get_object_or_404

from nolsatu_courses.apps.courses.models import Module, Section, TaskUploadSettings
from .forms import FormSection, FormTaskSetting


@staff_member_required
def index(request, id):
    module = get_object_or_404(Module, id=id)
    context = {
        'title': _('Daftar Bab'),
        'sections': module.sections.all(),
        'module': module,
        'sidebar': True
    }
    return render(request, 'backoffice/sections/index.html', context)


@staff_member_required
def add(request, id):
    module = get_object_or_404(Module, id=id)
    form = FormSection(data=request.POST or None, files=request.FILES or None, module=module)
    if form.is_valid():
        section = form.save()
        messages.success(request, _(f"Berhasil tambah bab {section.title}"))
        return redirect('backoffice:sections:index', id=id)

    context = {
        'title': _('Tambah Bab'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'backoffice/form-editor.html', context)


@staff_member_required
def edit(request, id):
    section = get_object_or_404(Section, id=id)
    form = FormSection(data=request.POST or None, files=request.FILES or None, instance=section)
    if form.is_valid():
        section = form.save()
        messages.success(request, _(f"Berhasil ubah bab {section.title}"))
        return redirect('backoffice:sections:index', id=section.module.id)

    context = {
        'title': _('Ubah Bab'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'backoffice/form-editor.html', context)


@staff_member_required
def delete(request, id):
    section = get_object_or_404(Section, id=id)
    section.delete()
    messages.success(request, 'Berhasil hapus bab')
    return redirect('backoffice:sections:index', id=section.module.id)


@staff_member_required
def details(request, id):
    section = get_object_or_404(Section, id=id)

    context = {
        'title': 'Detail Bab',
        'section': section,
        'task_setting': TaskUploadSettings.objects.filter(section=section).first()
    }
    return render(request, 'backoffice/sections/detail.html', context)


@staff_member_required
def task_setting(request, id):
    section = get_object_or_404(Section, id=id)
    task_setting = TaskUploadSettings.objects.filter(section=section).first()
    form = FormTaskSetting(data=request.POST or None, instance=task_setting or None)
    if form.is_valid():
        task_setting = form.save(commit=False)
        task_setting.section = section
        task_setting.save()
        form.save_m2m()
        messages.success(request, _(f"Berhasil ubah pengaturan tugas"))
        return redirect('backoffice:sections:index', id=section.module.id)

    context = {
        'title': _('Pengaturan Tugas'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'backoffice/form-editor.html', context)
