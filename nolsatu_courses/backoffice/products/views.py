import sweetify

from django.conf import settings
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.decorators import superuser_required
from nolsatu_courses.apps.products.models import Product
from .forms import ProductForm


@superuser_required
def index(request):
    context = {
        'menu_active': 'products',
        'title': _('Daftar Produk'),
        'products': Product.objects.all(),
        'sidebar': True
    }
    return render(request, 'backoffice/products/index.html', context)


@superuser_required
def add(request):
    form = ProductForm(data=request.POST or None)
    if form.is_valid():
        with transaction.atomic():
            product = form.save()
        sweetify.success(request, _(f"Berhasil tambah produk {product.course}"), button='OK', icon='success')
        return redirect('backoffice:products:index')

    context = {
        'menu_active': 'products',
        'title': _('Tambah Produk'),
        'form': form,
        'title_submit': 'Simpan'
    }

    return render(request, 'backoffice/products/form.html', context)


@superuser_required
def edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    form = ProductForm(data=request.POST or None, instance=product)
    if form.is_valid():
        with transaction.atomic():
            product = form.save()
        sweetify.success(request, _(f"Berhasil ubah produk {product.course}"), button='OK', icon='success')
        return redirect('backoffice:products:index')

    context = {
        'menu_active': 'products',
        'title': _('Ubah Produk'),
        'form': form,
        'title_submit': 'Simpan'
    }

    return render(request, 'backoffice/products/form.html', context)


@superuser_required
def delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    with transaction.atomic():
        product.delete()
    sweetify.success(request, 'Berhasil hapus produk', button='OK', icon='success')
    return redirect('backoffice:products:index')
