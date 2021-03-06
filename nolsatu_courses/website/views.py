import urllib.parse

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.courses.models import Courses, Enrollment


def index(request):
    courses = Courses.objects
    if not request.user.is_superuser:
        courses = courses.filter(is_visible=True, status=Courses.STATUS.publish)

    courses = courses.select_related('product').select_related('vendor')
    user_courses_id = Enrollment.user_courses_id_set(request.user)

    context = {
        'title': _('Daftar Materi'),
        'courses': [{
            'course': course,
            'has_enrolled': course.id in user_courses_id
        } for course in courses],
        'user_page': False
    }
    return render(request, 'website/index.html', context)


def search(request):
    search_query = request.GET.get("q", "")
    course_search = Courses.objects.filter(
        Q(title__icontains=search_query) | Q(description__icontains=search_query))
    if request.user and request.user.is_superuser:
        courses = course_search
    else:
        courses = course_search.filter(
            is_visible=True, status=Courses.STATUS.publish
        )

    context = {
        'title': _(f'Hasil Pencarian untuk "{search_query}"'),
        'search_query': search_query,
        'courses': [{
            'course': course,
            'has_enrolled': course.has_enrolled(request.user)
        } for course in courses],
        'progress_bar': False
    }

    return render(request, 'website/index.html', context)


@login_required
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


def error_404(request):
    return render(request, '404.html', {})


def error_500(request):
    return render(request, '500.html', {})
