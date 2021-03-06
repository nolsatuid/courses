import sweetify

from django.db import transaction
from django.forms import modelformset_factory
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from quiz.models import Category, SubCategory, Quiz, Sitting
from multichoice.models import MCQuestion, Answer
from .forms import CategoryForm, SubCategoryForm, MCQuestionForm, FormQuizVendor, FormFilterQuizzesVendor
from nolsatu_courses.apps.courses.models import Enrollment
from nolsatu_courses.apps.decorators import vendor_member_required



@vendor_member_required
def list_category(request):
    context = {
        'menu_active': 'quiz',
        'categories': Category.objects.filter(vendor__users__email=request.user.email),
        'title': _('Kategori Kuis'),
        'sidebar': True,
    }
    return render(request, 'vendors/quizzes/category.html', context)


@vendor_member_required
def create_category(request):
    form = CategoryForm(data=request.POST or None)
    if form.is_valid():
        category = form.save(commit=False)
        category.vendor = request.user.vendors.first()
        with transaction.atomic():
            category.save()
        sweetify.success(request, _(f"Berhasil tambah Kategori {category.category}"), button='OK', icon='success')
        return redirect('vendors:quizzes:category')

    context = {
        'menu_active': 'quiz',
        'title': _('Tambah Kategori'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'vendors/form-editor.html', context)


@vendor_member_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, vendor__users__email=request.user.email)
    form = CategoryForm(data=request.POST or None, instance=category)
    if form.is_valid():
        with transaction.atomic():
            category = form.save()
        sweetify.success(request, _(f"Berhasil ubah kategori {category.category}"), button='OK', icon='success')
        return redirect('vendors:quizzes:category')

    context = {
        'menu_active': 'quiz',
        'title': _('Ubah Kategori'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'vendors/form-editor.html', context)


@vendor_member_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, vendor__users__email=request.user.email)
    with transaction.atomic():
        category.delete()
    sweetify.success(request, 'Berhasil hapus Kategori', button='OK', icon='success')
    return redirect('vendors:quizzes:category')


@vendor_member_required
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


@vendor_member_required
def create_sub_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, vendor__users__email=request.user.email)

    form = SubCategoryForm(data=request.POST or None)
    if form.is_valid():
        sub_category = form.save(commit=False)
        sub_category.category = category
        with transaction.atomic():
            sub_category.save()
        sweetify.success(request, _(f"Berhasil tambah Sub Kategori {sub_category.sub_category}"), button='OK', icon='success')
        return redirect('vendors:quizzes:sub_category', category_id=category_id)

    context = {
        'menu_active': 'quiz',
        'title': _('Tambah Sub Kategori'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'vendors/form-editor.html', context)


@vendor_member_required
def delete_sub_category(request, sub_category_id):
    sub_category = get_object_or_404(SubCategory, id=sub_category_id,
                                     category__vendor__users__email=request.user.email)
    category_id = sub_category.category.id
    with transaction.atomic():
        sub_category.delete()
    sweetify.success(request, 'Berhasil hapus Sub Kategori', button='OK', icon='success')
    return redirect('vendors:quizzes:sub_category', category_id=category_id)


@vendor_member_required
def edit_sub_category(request, sub_category_id):
    sub_category = get_object_or_404(SubCategory, id=sub_category_id,
                                     category__vendor__users__email=request.user.email)
    form = SubCategoryForm(data=request.POST or None, instance=sub_category)
    if form.is_valid():
        with transaction.atomic():
            sub_category.save()
        sweetify.success(request, _(f"Berhasil Ubah Sub Kategori {sub_category.sub_category}"), button='OK', icon='success')
        return redirect('vendors:quizzes:sub_category', category_id=sub_category.category.id)

    context = {
        'menu_active': 'quiz',
        'title': _('Ubah Sub Kategori'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'vendors/form-editor.html', context)


@vendor_member_required
def list_question(request):
    context = {
        'menu_active': 'quiz',
        'questions': MCQuestion.objects.filter(vendor__users__email=request.user.email),
        'title': _('Pertanyaan Kuis'),
        'sidebar': True,
    }
    return render(request, 'vendors/quizzes/question.html', context)


@vendor_member_required
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


@vendor_member_required
def create_question(request):
    form = MCQuestionForm(data=request.POST or None, prefix='question')
    AnswerFormSet = modelformset_factory(Answer, extra=3, fields=('content', 'correct'), can_delete=True)
    formset = AnswerFormSet(data=request.POST or None, queryset=Answer.objects.none(), prefix='answer')
    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                question = form.save(request.user.vendors.first())

                instance = formset.save(commit=False)
                for obj in formset.deleted_objects:
                    obj.delete()
                for i in instance:
                    i.question = question
                    i.save()
            sweetify.success(request, _(f"Berhasil tambah Pertanyaan {question.content}"), button='OK', icon='success')
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


@vendor_member_required
def delete_question(request, question_id):
    category = get_object_or_404(MCQuestion, id=question_id, vendor__users__email=request.user.email)
    with transaction.atomic():
        category.delete()
    sweetify.success(request, 'Berhasil hapus Pertanyaan', button='OK', icon='success')
    return redirect('vendors:quizzes:question')


@vendor_member_required
def edit_question(request, question_id):
    data_question = get_object_or_404(MCQuestion, id=question_id, vendor__users__email=request.user.email)
    form = MCQuestionForm(data=request.POST or None, instance=data_question, prefix='question')

    AnswerFormSet = modelformset_factory(Answer, extra=3, fields=('content', 'correct'), can_delete=True)
    formset = AnswerFormSet(data=request.POST or None, queryset=Answer.objects.filter(
        question=data_question).all(), prefix='answer')

    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                question = form.save(request.user.vendors.first())

                instance = formset.save(commit=False)
                for obj in formset.deleted_objects:
                    obj.delete()
                for i in instance:
                    i.question = question
                    i.save()
            sweetify.success(request, _(f"Berhasil Ubah Pertanyaan {question.content}"), button='OK', icon='success')
            return redirect('vendors:quizzes:question')

    context = {
        'menu_active': 'quiz',
        'title': _('Ubah Pertanyaan'),
        'form': form,
        'formset': formset,
        'title_submit': 'Simpan',
        'code': 'question',
        'formset_delete': True,
    }
    return render(request, 'vendors/form-editor.html', context)


@vendor_member_required
def list_quiz(request):
    context = {
        'menu_active': 'quiz',
        'quizzes': Quiz.objects.filter(category__vendor__users__email=request.user.email),
        'title': _('Daftar Kuis'),
        'sidebar': True,
    }
    return render(request, 'vendors/quizzes/quiz.html', context)


@vendor_member_required
def create_quiz(request):
    form = FormQuizVendor(data=request.POST or None, user_email=request.user.email)
    if form.is_valid():
        quiz = form.save()
        sweetify.success(request, _(f"Berhasil tambah kuis {quiz.title}"), button='OK', icon='success')
        return redirect('vendors:quizzes:list_quiz')

    context = {
        'menu_active': 'quiz',
        'title': _('Tambah Kuis'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'vendors/form-quiz.html', context)


@vendor_member_required
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    form = FormQuizVendor(data=request.POST or None, instance=quiz, user_email=request.user.email)
    if form.is_valid():
        quiz = form.save()
        sweetify.success(request, _(f"Berhasil ubah kursus {quiz.title}"), button='OK', icon='success')
        return redirect('vendors:quizzes:list_quiz')

    context = {
        'menu_active': 'quiz',
        'title': _('Ubah Kuis'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'vendors/form-quiz.html', context)


@vendor_member_required
def result_quiz(request):
    quizzes = None
    batch = None
    download = request.GET.get('download', '')
    form = FormFilterQuizzesVendor(request.GET or None, user_email=request.user.email)
    if form.is_valid():
        batch = form.cleaned_data['batch']
        quizzes = form.get_data()
        if download:
            csv_buffer = form.download_report()
            response = HttpResponse(csv_buffer.getvalue(), content_type="text/csv")
            response['Content-Disposition'] = f'attachment; filename=Quiz-Angkatan{batch}.csv'
            return response

    context = {
        'menu_active': 'quiz',
        'title': _('Hasil Kuis'),
        'quizzes': quizzes,
        'form': form,
        'batch': batch.id if batch else None
    }
    return render(request, 'vendors/quizzes/results.html', context)


@vendor_member_required
def detail_result(request, quiz_id, batch_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, category__vendor__users__email=request.user.email)
    user_ids = Enrollment.objects.filter(batch_id=batch_id).values_list('user__id', flat=True)
    results = Sitting.objects.select_related('user', 'quiz') \
        .filter(quiz=quiz, user__id__in=user_ids).order_by('-current_score')

    context = {
        'menu_active': 'quiz',
        'title': _('Detail Hasil Kuis'),
        'quiz': quiz,
        'results': results,
        'batch': batch_id
    }
    return render(request, 'vendors/quizzes/detail-results.html', context)


@vendor_member_required
def participant_result(request, id, batch):
    sitting = get_object_or_404(Sitting.objects.select_related('user', 'quiz'), id=id,
                                quiz__category__vendor__users__email=request.user.email)

    context = {
        'menu_active': 'quiz',
        'title': _('Detail Hasil Partisipan'),
        'sitting': sitting,
        'questions': sitting.get_questions(with_answers=True),
        'batch': batch
    }
    return render(request, 'vendors/quizzes/participant-results.html', context)
