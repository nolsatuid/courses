from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required

from nolsatu_courses.apps.courses.models import Batch
from .forms import FormBatchVendor


@staff_member_required
def index(request):
    context = {
        'menu_active': 'batch',
        'title': _('Daftar Angkatan'),
        'batchs': Batch.objects.filter(course__vendor__users__email=request.user.email).select_related('course'),
        'sidebar': True
    }
    return render(request, 'vendors/batchs/index.html', context)


@staff_member_required
def create(request):
    form = FormBatchVendor(data=request.POST or None, user_email=request.user.email)
    if form.is_valid():
        with transaction.atomic():
            batch = form.save()
        messages.success(request, _(f"Berhasil tambah angkatan {batch.batch}"))
        return redirect('vendors:batchs:index')

    context = {
        'menu_active': 'batch',
        'title': _('Tambah Angkatan'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'vendors/form.html', context)


@staff_member_required
def details(request, id):
    batch = get_object_or_404(Batch, id=id, course__vendor__users__email=request.user.email)
    context = {
        'menu_active': 'batch',
        'title': 'Detail Angkatan',
        'batch': batch
    }
    return render(request, 'vendors/batchs/detail.html', context)
