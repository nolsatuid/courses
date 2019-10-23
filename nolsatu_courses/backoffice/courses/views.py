from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

from nolsatu_courses.apps.courses.models import Courses
from .forms import FormCourses


@staff_member_required
def index(request):
    context = {
        'title': _('Daftar Kursus'),
        'courses': Courses.objects.all()
    }
    return render(request, 'backoffice/courses/index.html', context)


@staff_member_required
def add(request):
    form = FormCourses(request.POST or None)
    if form.is_valid():
        course = form.save()
        messages.success(request, _(f"Berhasil Tambah Kursus {course.title}"))
        return redirect('backoffice:courses:index')

    context = {
        'title': _('Tambah Kursus'),
        'form': form
    }
    return render(request, 'backoffice/form.html', context)
