from django.contrib import messages
from django.db import transaction
from django.forms import formset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from quiz.models import Category, SubCategory
from multichoice.models import MCQuestion, Answer
from .forms import CategoryForm, SubCategoryForm, MCQuestionForm, AnswerForm, AnswerModelForm


@staff_member_required
def list_category(request):
    context = {
        'menu_active': 'quiz',
        'categories': Category.objects.filter(vendor__users__email=request.user.email),
        'title': _('Kategori Kuis'),
        'sidebar': True,
    }
    return render(request, 'vendors/quizzes/category.html', context)


@staff_member_required
def create_category(request):
    form = CategoryForm(data=request.POST or None)
    if form.is_valid():
        category = form.save(commit=False)
        category.vendor = request.user.vendors.first()
        with transaction.atomic():
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
        with transaction.atomic():
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
    with transaction.atomic():
        category.delete()
    messages.success(request, 'Berhasil hapus Kategori')
    return redirect('vendors:quizzes:category')


@staff_member_required
def list_sub_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, vendor__users__email=request.user.email)

    context = {
        'menu_active': 'quiz',
        'category': category,
        'sub_categories': SubCategory.objects.filter(category=category_id,
                                                     category__vendor__users__email=request.user.email),
        'title': _(f'Sub Kategori {category.category}'),
        'sidebar': True,
    }
    return render(request, 'vendors/quizzes/sub-category.html', context)


@staff_member_required
def create_sub_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, vendor__users__email=request.user.email)

    form = SubCategoryForm(data=request.POST or None)
    if form.is_valid():
        sub_category = form.save(commit=False)
        sub_category.category = category
        with transaction.atomic():
            sub_category.save()
        messages.success(request, _(f"Berhasil tambah Sub Kategori {sub_category.sub_category}"))
        return redirect('vendors:quizzes:sub_category', category_id=category_id)

    context = {
        'menu_active': 'quiz',
        'title': _('Tambah Sub Kategori'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'vendors/form-editor.html', context)


@staff_member_required
def delete_sub_category(request, sub_category_id):
    sub_category = get_object_or_404(SubCategory, id=sub_category_id,
                                     category__vendor__users__email=request.user.email)
    category_id = sub_category.category.id
    with transaction.atomic():
        sub_category.delete()
    messages.success(request, 'Berhasil hapus Sub Kategori')
    return redirect('vendors:quizzes:sub_category', category_id=category_id)


@staff_member_required
def edit_sub_category(request, sub_category_id):
    sub_category = get_object_or_404(SubCategory, id=sub_category_id,
                                     category__vendor__users__email=request.user.email)
    form = SubCategoryForm(data=request.POST or None, instance=sub_category)
    if form.is_valid():
        with transaction.atomic():
            sub_category.save()
        messages.success(request, _(f"Berhasil Ubah Sub Kategori {sub_category.sub_category}"))
        return redirect('vendors:quizzes:sub_category', category_id=sub_category.category.id)

    context = {
        'menu_active': 'quiz',
        'title': _('Ubah Sub Kategori'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'vendors/form-editor.html', context)


@staff_member_required
def list_question(request):
    context = {
        'menu_active': 'quiz',
        'questions': MCQuestion.objects.filter(vendor__users__email=request.user.email),
        'title': _('Pertanyaan Kuis'),
        'sidebar': True,
    }
    return render(request, 'vendors/quizzes/question.html', context)


@staff_member_required
def ajax_filter_subcategory(request):
    category = request.GET.get('category', None)
    data = {
        'sub_category': []
    }
    if category:
        sub_category = SubCategory.objects.filter(category=category)
        data['sub_category'] = [
            {
                'id': sub.id,
                'sub_category': sub.sub_category
            } for sub in sub_category
        ]

    return JsonResponse(data, status=200)


@staff_member_required
def create_question(request):
    form = MCQuestionForm(prefix='question')
    AnswerFormSet = formset_factory(AnswerForm, extra=3)
    formset = AnswerFormSet(prefix='answer')
    if request.method == 'POST':
        form = MCQuestionForm(data=request.POST, prefix='question')
        formset = AnswerFormSet(data=request.POST, prefix='answer')
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                question = form.save(request.user.vendors.first())
                answer = [form.cleaned_data for form in formset]
                for x in answer:
                    AnswerModelForm(x).save(question)
            messages.success(request, _(f"Berhasil tambah Pertanyaan {question.content}"))
            return redirect('vendors:quizzes:question')

    context = {
        'menu_active': 'quiz',
        'title': _('Tambah Pertanyaan'),
        'form': form,
        'formset': formset,
        'title_submit': 'Simpan',
        'code': 'question',
        'formset_delete': False,
    }
    return render(request, 'vendors/form-editor.html', context)


@staff_member_required
def delete_question(request, question_id):
    category = get_object_or_404(MCQuestion, id=question_id, vendor__users__email=request.user.email)
    with transaction.atomic():
        category.delete()
    messages.success(request, 'Berhasil hapus Pertanyaan')
    return redirect('vendors:quizzes:question')
