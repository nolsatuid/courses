from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from quiz.models import Category
from .forms import CategoryForm


@staff_member_required
def list_category(request):
    form = CategoryForm()
    context = {
        'menu_active': 'quiz',
        'categories': Category.objects.filter(vendor__users__email=request.user.email),
        'title': _('Kategori Kuis'),
        'sidebar': True,
        'form': form
    }
    return render(request, 'vendors/quizzes/category.html', context)


@staff_member_required
def create_category(request):
    form = CategoryForm(data=request.POST or None)
    if form.is_valid():
        category = form.save(commit=False)
        category.vendor = request.user.vendors.first()
        category.save()
        messages.success(request, _(f"Berhasil tambah Kategori {category.category}"))
        return redirect('vendors:quizzes:category')

    context = {
        'menu_active': 'quiz',
        'title': _('Tambah Kategori'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'vendors/form-editor.html', context)


@staff_member_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, vendor__users__email=request.user.email)
    form = CategoryForm(data=request.POST or None, instance=category)
    if form.is_valid():
        category = form.save()
        messages.success(request, _(f"Berhasil ubah kategori {category.category}"))
        return redirect('vendors:quizzes:category')

    context = {
        'menu_active': 'quiz',
        'title': _('Ubah Kategori'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'vendors/form-editor.html', context)


@staff_member_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, vendor__users__email=request.user.email)
    category.delete()
    messages.success(request, 'Berhasil hapus Kategori')
    return redirect('vendors:quizzes:category')


