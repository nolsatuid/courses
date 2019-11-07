from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import get_object_or_404

from nolsatu_courses.apps.courses.models import Courses
from .forms import FormCourses


@staff_member_required
def index(request):
    context = {
        'title': _('Daftar Kursus'),
        'courses': Courses.objects.all(),
        'sidebar': True
    }
    return render(request, 'backoffice/courses/index.html', context)


@staff_member_required
def add(request):
    form = FormCourses(data=request.POST or None, files=request.FILES or None)
    if form.is_valid():
        course = form.save()
        messages.success(request, _(f"Berhasil tambah kursus {course.title}"))
        return redirect('backoffice:courses:index')

    context = {
        'title': _('Tambah Kursus'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'backoffice/form-editor.html', context)


@staff_member_required
def edit(request, id):
    course = get_object_or_404(Courses, id=id)
    form = FormCourses(data=request.POST or None, files=request.FILES or None, instance=course)
    if form.is_valid():
        course = form.save()
        messages.success(request, _(f"Berhasil ubah kursus {course.title}"))
        return redirect('backoffice:courses:index')

    context = {
        'title': _('Ubah Kursus'),
        'form': form,
        'title_submit': 'Simpan'
    }
    return render(request, 'backoffice/form-editor.html', context)


@staff_member_required
def delete(request, id):
    course = get_object_or_404(Courses, id=id)
    course.delete()
    messages.success(request, 'Berhasil hapus kursus')
    return redirect('backoffice:courses:index')


@staff_member_required
def details(request, id):
    course = get_object_or_404(Courses, id=id)

    context = {
        'title': 'Detail Kursus',
        'course': course
    }
    return render(request, 'backoffice/courses/detail.html', context)
