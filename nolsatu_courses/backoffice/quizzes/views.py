from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import get_object_or_404

from quiz.models import Quiz, Sitting
from quiz.admin import QuizAdminForm


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
    form = QuizAdminForm(data=request.POST or None)
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
    return render(request, 'backoffice/form.html', context)


@staff_member_required
def edit(request, id):
    quiz = get_object_or_404(Quiz, id=id)
    form = QuizAdminForm(data=request.POST or None, instance=quiz)
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
    return render(request, 'backoffice/form.html', context)


@staff_member_required
def results(request):
    quizzes = Quiz.objects.all()

    context = {
        'menu_active': 'quiz',
        'title': _('Hasil Kuis'),
        'quizzes': quizzes
    }
    return render(request, 'backoffice/quizzes/results.html', context)


@staff_member_required
def detail_result(request, id):
    quiz = get_object_or_404(Quiz, id=id)
    results = Sitting.objects.filter(quiz=quiz).order_by('-current_score')

    context = {
        'menu_active': 'quiz',
        'title': _('Detail Hasil Kuis'),
        'quiz': quiz,
        'results': results
    }
    return render(request, 'backoffice/quizzes/detail-results.html', context)


@staff_member_required
def participant_result(request, id):
    sitting = get_object_or_404(Sitting, id=id)

    context = {
        'menu_active': 'quiz',
        'title': _('Detail Hasil Partisipan'),
        'sitting': sitting,
        'questions': sitting.get_questions(with_answers=True)
    }
    return render(request, 'backoffice/quizzes/participant-results.html', context)
