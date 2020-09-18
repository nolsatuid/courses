import sweetify

from django.db import transaction
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.forms import modelformset_factory

from quiz.models import Quiz, Sitting, Question, SubCategory, Category
from nolsatu_courses.apps.courses.models import Enrollment
from nolsatu_courses.apps.decorators import superuser_required
from multichoice.models import MCQuestion, Answer
from nolsatu_courses.vendors.quizzes.forms import SubCategoryForm
from .forms import FormQuiz, FormFilterQuizzes, CategoryFormBackoffice, MCQuestionFormBackoffice


@superuser_required
def index(request):
    context = {
        'menu_active': 'quiz',
        'title': _('Daftar Kuis'),
        'quizzes': Quiz.objects.all(),
        'sidebar': True
    }
    return render(request, 'backoffice/quizzes/index.html', context)


@superuser_required
def add(request):
    form = FormQuiz(data=request.POST or None)
    if form.is_valid():
        quiz = form.save()
        sweetify.success(request, _(f"Berhasil tambah kuis {quiz.title}"), button='OK', icon='success')
        return redirect('backoffice:quizzes:index')

    context = {
        'menu_active': 'quiz',
        'title': _('Tambah Kuis'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'backoffice/form-quiz.html', context)


@superuser_required
def edit(request, id):
    quiz = get_object_or_404(Quiz, id=id)
    form = FormQuiz(data=request.POST or None, instance=quiz)
    if form.is_valid():
        quiz = form.save()
        sweetify.success(request, _(f"Berhasil ubah kursus {quiz.title}"), button='OK', icon='success')
        return redirect('backoffice:quizzes:index')

    context = {
        'menu_active': 'quiz',
        'title': _('Ubah Kuis'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'backoffice/form-quiz.html', context)


@superuser_required
def results(request):
    quizzes = None
    batch = None
    download = request.GET.get('download', '')
    form = FormFilterQuizzes(request.GET or None)
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
    return render(request, 'backoffice/quizzes/results.html', context)


@superuser_required
def detail_result(request, id, batch):
    quiz = get_object_or_404(Quiz, id=id)
    user_ids = Enrollment.objects.filter(batch_id=batch).values_list('user__id', flat=True)
    results = Sitting.objects.select_related('user', 'quiz') \
        .filter(quiz=quiz, user__id__in=user_ids).order_by('-current_score')

    context = {
        'menu_active': 'quiz',
        'title': _('Detail Hasil Kuis'),
        'quiz': quiz,
        'results': results,
        'batch': batch
    }
    return render(request, 'backoffice/quizzes/detail-results.html', context)


@superuser_required
def participant_result(request, id, batch):
    sitting = get_object_or_404(Sitting.objects.select_related('user', 'quiz'), id=id)

    context = {
        'menu_active': 'quiz',
        'title': _('Detail Hasil Partisipan'),
        'sitting': sitting,
        'questions': sitting.get_questions(with_answers=True),
        'batch': batch
    }
    return render(request, 'backoffice/quizzes/participant-results.html', context)


@superuser_required
def ajax_filter_sub_category(request):
    category = request.GET.get('category', None)
    data = {
        'sub_category': []
    }
    if category:
        sub_category = SubCategory.objects.filter(category=category)
        data['sub_category'] = [
            {
                'id': s.id,
                'name': s.sub_category
            } for s in sub_category
        ]

    return JsonResponse(data, status=200)


@superuser_required
def ajax_filter_questions(request):
    sub_category = request.GET.get('sub_category', None)
    data = {
        'questions': []
    }
    questions = Question.objects.all()
    if sub_category:
        questions = questions.filter(sub_category=sub_category)

    data['questions'] = [
        {
            'id': s.id,
            'name': s.content
        } for s in questions
    ]

    return JsonResponse(data, status=200)


@superuser_required
def participant_result(request, id, batch):
    sitting = get_object_or_404(Sitting.objects.select_related('user', 'quiz'), id=id)

    context = {
        'menu_active': 'quiz',
        'title': _('Detail Hasil Partisipan'),
        'sitting': sitting,
        'questions': sitting.get_questions(with_answers=True),
        'batch': batch
    }
    return render(request, 'backoffice/quizzes/participant-results.html', context)


@superuser_required
def list_category(request):
    context = {
        'menu_active': 'quiz',
        'categories': Category.objects.all(),
        'title': _('Kategori Kuis'),
        'sidebar': True,
    }
    return render(request, 'backoffice/quizzes/category.html', context)


@superuser_required
def create_category(request):
    form = CategoryFormBackoffice(data=request.POST or None)
    if form.is_valid():
        with transaction.atomic():
            category = form.save()
        sweetify.success(request, _(f"Berhasil tambah Kategori {category.category}"), button='OK', icon='success')
        return redirect('backoffice:quizzes:category')

    context = {
        'menu_active': 'quiz',
        'title': _('Tambah Kategori'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'backoffice/form-editor.html', context)


@superuser_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    form = CategoryFormBackoffice(data=request.POST or None, instance=category)
    if form.is_valid():
        with transaction.atomic():
            category = form.save()
        sweetify.success(request, _(f"Berhasil ubah kategori {category.category}"), button='OK', icon='success')
        return redirect('backoffice:quizzes:category')

    context = {
        'menu_active': 'quiz',
        'title': _('Ubah Kategori'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'backoffice/form-editor.html', context)


@superuser_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    with transaction.atomic():
        category.delete()
    sweetify.success(request, 'Berhasil hapus Kategori', button='OK', icon='success')
    return redirect('backoffice:quizzes:category')


@superuser_required
def list_sub_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    context = {
        'menu_active': 'quiz',
        'category': category,
        'sub_categories': SubCategory.objects.filter(category=category_id),
        'title': _(f'Sub Kategori {category.category}'),
        'sidebar': True,
    }
    return render(request, 'backoffice/quizzes/sub-category.html', context)


@superuser_required
def create_sub_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    form = SubCategoryForm(data=request.POST or None)
    if form.is_valid():
        sub_category = form.save(commit=False)
        sub_category.category = category
        with transaction.atomic():
            sub_category.save()
        sweetify.success(request, _(f"Berhasil tambah Sub Kategori {sub_category.sub_category}"), button='OK', icon='success')
        return redirect('backoffice:quizzes:sub_category', category_id=category_id)

    context = {
        'menu_active': 'quiz',
        'title': _('Tambah Sub Kategori'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'backoffice/form-editor.html', context)


@superuser_required
def delete_sub_category(request, sub_category_id):
    sub_category = get_object_or_404(SubCategory, id=sub_category_id)
    category_id = sub_category.category.id
    with transaction.atomic():
        sub_category.delete()
    sweetify.success(request, 'Berhasil hapus Sub Kategori', button='OK', icon='success')
    return redirect('backoffice:quizzes:sub_category', category_id=category_id)


@superuser_required
def edit_sub_category(request, sub_category_id):
    sub_category = get_object_or_404(SubCategory, id=sub_category_id,)
    form = SubCategoryForm(data=request.POST or None, instance=sub_category)
    if form.is_valid():
        with transaction.atomic():
            sub_category.save()
        sweetify.success(request, _(f"Berhasil Ubah Sub Kategori {sub_category.sub_category}"), button='OK', icon='success')
        return redirect('backoffice:quizzes:sub_category', category_id=sub_category.category.id)

    context = {
        'menu_active': 'quiz',
        'title': _('Ubah Sub Kategori'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'backoffice/form-editor.html', context)


@superuser_required
def ajax_filter_category(request):
    vendor = request.GET.get('vendor', None)
    data = {
        'category': []
    }
    if vendor:
        category = Category.objects.filter(vendor=vendor)
        data['category'] = [
            {
                'id': cat.id,
                'category': cat.category
            } for cat in category
        ]

    return JsonResponse(data, status=200)


@superuser_required
def list_question(request):
    context = {
        'menu_active': 'quiz',
        'questions': MCQuestion.objects.all(),
        'title': _('Pertanyaan Kuis'),
        'sidebar': True,
    }
    return render(request, 'backoffice/quizzes/question.html', context)


@superuser_required
def create_question(request):
    form = MCQuestionFormBackoffice(data=request.POST or None, prefix='question')
    AnswerFormSet = modelformset_factory(Answer, extra=3, fields=('content', 'correct'), can_delete=True)
    formset = AnswerFormSet(data=request.POST or None, queryset=Answer.objects.none(), prefix='answer')
    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                question = form.save()

                instance = formset.save(commit=False)
                for obj in formset.deleted_objects:
                    obj.delete()
                for i in instance:
                    i.question = question
                    i.save()
            sweetify.success(request, _(f"Berhasil tambah Pertanyaan {question.content}"), button='OK', icon='success')
            return redirect('backoffice:quizzes:question')

    context = {
        'menu_active': 'quiz',
        'title': _('Tambah Pertanyaan'),
        'form': form,
        'formset': formset,
        'title_submit': 'Simpan',
        'code': 'question',
        'formset_delete': False,
    }
    return render(request, 'backoffice/form-editor.html', context)


@superuser_required
def delete_question(request, question_id):
    category = get_object_or_404(MCQuestion, id=question_id)
    with transaction.atomic():
        category.delete()
    sweetify.success(request, 'Berhasil hapus Pertanyaan', button='OK', icon='success')
    return redirect('backoffice:quizzes:question')


@superuser_required
def edit_question(request, question_id):
    data_question = get_object_or_404(MCQuestion, id=question_id)
    form = MCQuestionFormBackoffice(data=request.POST or None, instance=data_question, prefix='question')

    AnswerFormSet = modelformset_factory(Answer, extra=3, fields=('content', 'correct'), can_delete=True)
    formset = AnswerFormSet(data=request.POST or None, queryset=Answer.objects.filter(
        question=data_question).all(), prefix='answer')

    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                question = form.save()

                instance = formset.save(commit=False)
                for obj in formset.deleted_objects:
                    obj.delete()
                for i in instance:
                    i.question = question
                    i.save()
            sweetify.success(request, _(f"Berhasil Ubah Pertanyaan {question.content}"), button='OK', icon='success')
            return redirect('backoffice:quizzes:question')

    context = {
        'menu_active': 'quiz',
        'title': _('Ubah Pertanyaan'),
        'form': form,
        'formset': formset,
        'title_submit': 'Simpan',
        'code': 'question',
        'formset_delete': True,
    }
    return render(request, 'backoffice/form-editor.html', context)