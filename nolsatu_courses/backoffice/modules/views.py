from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import get_object_or_404

from nolsatu_courses.apps.courses.models import Courses, Module
from .forms import FormModule


@staff_member_required
def index(request, id):
    course = get_object_or_404(Courses, id=id)
    context = {
        'title': _('Daftar Modul'),
        'modules': Module.objects.all(),
        'course': course,
        'sidebar': True
    }
    return render(request, 'backoffice/modules/index.html', context)


@staff_member_required
def add(request, id):
    course = get_object_or_404(Courses, id=id)
    form = FormModule(data=request.POST or None, files=request.FILES or None, course=course)
    if form.is_valid():
        module = form.save()
        messages.success(request, _(f"Berhasil tambah modul {module.title}"))
        return redirect('backoffice:modules:index', id=id)

    context = {
        'title': _('Tambah Modul'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'backoffice/form-editor.html', context)


@staff_member_required
def edit(request, id):
    module = get_object_or_404(Module, id=id)
    form = FormModule(data=request.POST or None, files=request.FILES or None, instance=module)
    if form.is_valid():
        module = form.save()
        messages.success(request, _(f"Berhasil ubah modul {module.title}"))
        return redirect('backoffice:modules:index', id=module.course.id)

    context = {
        'title': _('Ubah Modul'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'backoffice/form-editor.html', context)


@staff_member_required
def delete(request, id):
    module = get_object_or_404(Module, id=id)
    module.delete()
    messages.success(request, 'Berhasil hapus modul')
    return redirect('backoffice:modules:index', id=module.course.id)


@staff_member_required
def details(request, id):
    module = get_object_or_404(Module, id=id)

    context = {
        'title': 'Detail Modul',
        'module': module
    }
    return render(request, 'backoffice/modules/detail.html', context)
