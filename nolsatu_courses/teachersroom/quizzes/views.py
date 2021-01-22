from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, get_object_or_404

from nolsatu_courses.apps.decorators import superuser_required, teacher_required
from quiz.models import Quiz, Sitting
from .forms import TrainerFormFilterQuizzes
from ...apps.courses.models import Enrollment, Batch


@teacher_required
def results(request):
    quizzes = None
    batch = None
    form = TrainerFormFilterQuizzes(request.GET or None, user_email=request.user.email)
    if form.is_valid():
        batch = form.cleaned_data['batch']
        quizzes = form.get_data()

    context = {
        'menu_active': 'quiz',
        'title': _('Hasil Kuis'),
        'quizzes': quizzes,
        'form': form,
        'batch': batch.id if batch else None
    }
    return render(request, 'teachersroom/quizzes/results.html', context)


@teacher_required
def detail_result(request, id, batch):
    quiz = get_object_or_404(Quiz, id=id, courses__batchs__teaches__user__email=request.user.email)
    batch_trainer = get_object_or_404(Batch, id=batch, teaches__user__email=request.user.email)

    user_ids = Enrollment.objects.filter(batch_id=batch_trainer).values_list('user__id', flat=True)
    results_quiz = (Sitting.objects.select_related('user', 'quiz')
                    .filter(quiz=quiz, user__id__in=user_ids).order_by('-current_score'))

    context = {
        'menu_active': 'quiz',
        'title': _('Detail Hasil Kuis'),
        'quiz': quiz,
        'results': results_quiz,
        'batch': batch_trainer
    }
    return render(request, 'teachersroom/quizzes/detail-results.html', context)
