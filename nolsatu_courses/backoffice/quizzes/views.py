from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404

from quiz.models import Quiz, Sitting


@staff_member_required
def index(request):
    quizzes = Quiz.objects.all()

    context = {
        'menu_active': 'quiz',
        'title': _('Hasil Kuis'),
        'quizzes': quizzes
    }
    return render(request, 'backoffice/quizzes/index.html', context)


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
