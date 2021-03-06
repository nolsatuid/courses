import sweetify

from django.db import transaction
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.courses.models import Batch
from nolsatu_courses.apps.decorators import vendor_member_required
from .forms import FormBatchVendor


@vendor_member_required
def index(request):
    context = {
        'menu_active': 'batch',
        'title': _('Daftar Angkatan'),
        'batchs': Batch.objects.filter(course__vendor__users__email=request.user.email).select_related('course'),
        'sidebar': True
    }
    return render(request, 'vendors/batchs/index.html', context)


@vendor_member_required
def create(request):
    form = FormBatchVendor(data=request.POST or None, user_email=request.user.email)
    if form.is_valid():
        with transaction.atomic():
            batch = form.save()
        sweetify.success(request, _(f"Berhasil tambah angkatan {batch.batch}"), button='OK', icon='success')
        return redirect('vendors:batchs:index')

    context = {
        'menu_active': 'batch',
        'title': _('Tambah Angkatan'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'vendors/form.html', context)


@vendor_member_required
def details(request, id):
    batch = get_object_or_404(Batch, id=id, course__vendor__users__email=request.user.email)
    context = {
        'menu_active': 'batch',
        'title': 'Detail Angkatan',
        'batch': batch
    }
    return render(request, 'vendors/batchs/detail.html', context)


@vendor_member_required
def edit(request, id):
    batch = get_object_or_404(Batch, id=id, course__vendor__users__email=request.user.email)
    form = FormBatchVendor(data=request.POST or None, instance=batch, user_email=request.user.email)
    if form.is_valid():
        with transaction.atomic():
            batch = form.save()
        sweetify.success(request, _(f"Berhasil ubah angkatan {batch.batch}"), button='OK', icon='success')
        return redirect('vendors:batchs:index')

    context = {
        'menu_active': 'batch',
        'title': _('Ubah Angkatan'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'vendors/form.html', context)


@vendor_member_required
def delete(request, id):
    batch = get_object_or_404(Batch, id=id, course__vendor__users__email=request.user.email)
    with transaction.atomic():
        batch.delete()
    sweetify.success(request, 'Berhasil hapus angkatan', button='OK', icon='success')
    return redirect('vendors:batchs:index')
