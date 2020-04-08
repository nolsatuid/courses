from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import get_object_or_404

from nolsatu_courses.apps import utils
from nolsatu_courses.apps.courses.models import Batch
from .forms import FormBatch


@staff_member_required
def index(request):
    context = {
        'menu_active': 'batch',
        'title': _('Daftar Angkatan'),
        'batchs': Batch.objects.all(),
        'sidebar': True
    }
    return render(request, 'backoffice/batchs/index.html', context)


@staff_member_required
def add(request):
    form = FormBatch(data=request.POST or None, files=request.FILES or None)
    if form.is_valid():
        batch = form.save()
        messages.success(request, _(f"Berhasil tambah angkatan {batch.batch}"))
        return redirect('backoffice:batchs:index')

    context = {
        'menu_active': 'batch',
        'title': _('Tambah Angkatan'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'backoffice/form.html', context)


@staff_member_required
def edit(request, id):
    batch = get_object_or_404(Batch, id=id)
    form = FormBatch(data=request.POST or None, files=request.FILES or None, instance=batch)
    if form.is_valid():
        batch = form.save()
        messages.success(request, _(f"Berhasil ubah angkatan {batch.batch}"))
        return redirect('backoffice:batchs:index')

    context = {
        'menu_active': 'batch',
        'title': _('Ubah Angakatn'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'backoffice/form.html', context)


@staff_member_required
def delete(request, id):
    batch = get_object_or_404(Batch, id=id)
    batch.delete()
    messages.success(request, 'Berhasil hapus angkatan')
    return redirect('backoffice:batchs:index')


@staff_member_required
def details(request, id):
    batch = get_object_or_404(Batch, id=id)

    context = {
        'menu_active': 'batch',
        'title': 'Detail Angkatan',
        'batch': batch
    }
    return render(request, 'backoffice/batchs/detail.html', context)
