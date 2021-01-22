from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render

from nolsatu_courses.apps.decorators import superuser_required
from .forms import TrainerFormFilterQuizzes


@superuser_required
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