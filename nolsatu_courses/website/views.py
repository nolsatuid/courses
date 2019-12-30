import urllib.parse

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.courses.models import Courses


def index(request):
    context = {
        'title': _('Daftar Materi'),
        'courses': Courses.objects.all(),
        'progress_bar': False
    }
    return render(request, 'website/index.html', context)


def search(request):
    search_query = request.GET.get("q", "")

    context = {
        'title': _(f'Hasil Pencarian untuk "{search_query}"'),
        'search_query': search_query,
        'courses': Courses.objects.filter(Q(title__contains=search_query) | Q(description__contains=search_query)),
        'progress_bar': False
    }
    return render(request, 'website/index.html', context)


@login_required()
def logout(request):
    params = urllib.parse.urlencode({
        'next': settings.LOGOUT_REDIRECT_URL
    })
    return redirect(f'{settings.LOGOUT_URL}?{params}')


@login_required
def login(request):
    return redirect("website:index")


@login_required
def test_login(request):
    context = {
        'title': _('Kursus'),
        'courses': Courses.objects.all()
    }
    return render(request, 'website/index.html', context)
