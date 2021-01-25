import sweetify

from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from nolsatu_courses.apps.decorators import superuser_required
from nolsatu_courses.apps.courses.models import Batch, Teach
from .forms import FormBatch, FormAssignInstructor


@superuser_required
def index(request):
    context = {
        'menu_active': 'batch',
        'title': _('Daftar Kelas'),
        'batchs': Batch.objects.select_related('course'),
        'sidebar': True
    }
    return render(request, 'backoffice/batchs/index.html', context)


@superuser_required
def add(request):
    form = FormBatch(data=request.POST or None)
    if form.is_valid():
        batch = form.save()
        sweetify.success(request, _(f"Berhasil tambah kelas"), button='OK', icon='success')
        return redirect('backoffice:batchs:index')

    context = {
        'menu_active': 'batch',
        'title': _('Tambah Kelas'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'backoffice/form.html', context)


@superuser_required
def edit(request, id):
    batch = get_object_or_404(Batch, id=id)
    form = FormBatch(data=request.POST or None, instance=batch)
    if form.is_valid():
        batch = form.save()
        sweetify.success(request, _(f"Berhasil ubah kelas"), button='OK', icon='success')
        return redirect('backoffice:batchs:index')

    context = {
        'menu_active': 'batch',
        'title': _('Ubah Kelas'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'backoffice/form.html', context)


@superuser_required
def delete(request, id):
    batch = get_object_or_404(Batch, id=id)
    batch.delete()
    sweetify.success(request, 'Berhasil hapus kelas', button='OK', icon='success')
    return redirect('backoffice:batchs:index')


@superuser_required
def details(request, id):
    batch = get_object_or_404(Batch, id=id)

    context = {
        'menu_active': 'batch',
        'title': 'Detail Kelas',
        'batch': batch
    }
    return render(request, 'backoffice/batchs/detail.html', context)


@superuser_required
def assign_instructor(request, id):
    batch = get_object_or_404(Batch, id=id)
    form = FormAssignInstructor(data=request.POST or None, batch=batch)
    if form.is_valid():
        form.save(batch)
        sweetify.success(request, _(f"Berhasil menetapkan instruktur"), button='OK', icon='success')
        return redirect('backoffice:batchs:index')

    context = {
        'menu_active': 'batch',
        'title': _('Instruktur Kelas'),
        'form': form,
        'title_submit': 'Simpan',
        'batch': batch
    }
    return render(request, 'backoffice/form-assign-instructor.html', context)
