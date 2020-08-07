from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse

from quiz.models import Quiz, Sitting, Question, SubCategory
from nolsatu_courses.apps.courses.models import Enrollment
from .forms import FormQuiz, FormFilterQuizzes


@staff_member_required
def index(request):
    context = {
        'menu_active': 'quiz',
        'title': _('Daftar Kuis'),
        'quizzes': Quiz.objects.all(),
        'sidebar': True
    }
    return render(request, 'backoffice/quizzes/index.html', context)


@staff_member_required
def add(request):
    form = FormQuiz(data=request.POST or None)
    if form.is_valid():
        quiz = form.save()
        messages.success(request, _(f"Berhasil tambah kuis {quiz.title}"))
        return redirect('backoffice:quizzes:index')

    context = {
        'menu_active': 'quiz',
        'title': _('Tambah Kuis'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'backoffice/form-quiz.html', context)


@staff_member_required
def edit(request, id):
    quiz = get_object_or_404(Quiz, id=id)
    form = FormQuiz(data=request.POST or None, instance=quiz)
    if form.is_valid():
        quiz = form.save()
        messages.success(request, _(f"Berhasil ubah kursus {quiz.title}"))
        return redirect('backoffice:quizzes:index')

    context = {
        'menu_active': 'quiz',
        'title': _('Ubah Kuis'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'backoffice/form-quiz.html', context)


@staff_member_required
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


@staff_member_required
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


@staff_member_required
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


@staff_member_required
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


@staff_member_required
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


@staff_member_required
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