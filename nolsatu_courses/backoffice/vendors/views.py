from django.conf import settings
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from nolsatu_courses.apps.decorators import superuser_required
from nolsatu_courses.apps.vendors.models import Vendor
from .forms import VendorForm


@superuser_required
def index(request):
    context = {
        'menu_active': 'vendors',
        'title': _('Daftar Vendors'),
        'vendors': Vendor.objects.all(),
        'sidebar': True
    }
    return render(request, 'backoffice/vendors/index.html', context)


@superuser_required
def add(request):
    form = VendorForm(data=request.POST or None, files=request.FILES or None)
    if form.is_valid():
        with transaction.atomic():
            vendor = form.save()
        messages.success(request, _(f"Berhasil tambah vendor {vendor.name}"))
        return redirect('backoffice:vendors:index')

    context = {
        'menu_active': 'vendors',
        'title': _('Tambah Vendor'),
        'form': form,
        'title_submit': 'Simpan'
    }

    return render(request, 'backoffice/form-editor.html', context)


@superuser_required
def edit(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    form = VendorForm(data=request.POST or None, files=request.FILES or None, instance=vendor)
    if form.is_valid():
        with transaction.atomic():
            vendor = form.save()
        messages.success(request, _(f"Berhasil ubah kursus {vendor.name}"))
        return redirect('backoffice:vendors:index')

    context = {
        'menu_active': 'vendors',
        'title': _('Ubah Kursus'),
        'form': form,
        'title_submit': 'Simpan'
    }

    return render(request, 'backoffice/form-editor.html', context)


@superuser_required
def delete(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    with transaction.atomic():
        vendor.delete()
    messages.success(request, 'Berhasil hapus vendor')
    return redirect('backoffice:vendors:index')
