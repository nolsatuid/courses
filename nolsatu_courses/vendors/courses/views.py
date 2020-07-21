from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.courses.models import Courses
from nolsatu_courses.apps.vendors.models import Vendor
from nolsatu_courses.vendors.courses.forms import FormVendorCourse


@staff_member_required
def index(request):
    context = {
        'courses': Courses.objects.filter(vendor__users__email=request.user.email),
        'menu_active': 'course',
        'title': _('Daftar Kursus'),
        'sidebar': True
    }
    return render(request, 'vendors/courses/list.html', context)


@staff_member_required
def details(request, courses_id):
    course = get_object_or_404(Courses, id=courses_id, vendor__users__email=request.user.email)
    context = {
        'menu_active': 'course',
        'title': 'Detail Kursus',
        'course': course,
    }
    return render(request, 'vendors/courses/detail.html', context)


@staff_member_required
def create(request):
    template_name = 'vendors/form-editor.html'

    form = FormVendorCourse(data=request.POST or None, files=request.FILES or None)
    author = User.objects.filter(email=request.user.email).first()

    if form.is_valid():
        with transaction.atomic():
            course = form.save(author)
            form.save_m2m()
            messages.success(request, _(f"Berhasil tambah kursus {course.title}"))
        return redirect('vendors:courses:index')

    context = {
        'menu_active': 'course',
        'title': _('Tambah Kursus'),
        'form': form,
        'title_submit': 'Simpan'
    }

    if settings.FEATURE["MARKDOWN_VENDORS_EDITOR"]:
        template_name = 'vendors/form-editor-markdown.html'

    return render(request, template_name, context)


@staff_member_required
def delete(request, id):
    course = get_object_or_404(Courses, id=id, vendor__users__email=request.user.email)
    course.delete()
    messages.success(request, 'Berhasil hapus kursus')
    return redirect('vendors:courses:index')


@staff_member_required
def edit(request, id):
    template_name = 'vendors/form-editor.html'
    course = get_object_or_404(Courses, id=id, vendor__users__email=request.user.email)
    author = User.objects.filter(email=request.user.email).first()
    form = FormVendorCourse(data=request.POST or None, files=request.FILES or None, instance=course)

    if form.is_valid():
        with transaction.atomic():
            change_course = form.save(author)
            form.save_m2m()
        messages.success(request, _(f"Berhasil ubah kursus {change_course.title}"))
        return redirect('vendors:courses:index')

    context = {
        'menu_active': 'course',
        'title': _('Ubah Kursus'),
        'form': form,
        'title_submit': 'Simpan'
    }

    if settings.FEATURE["MARKDOWN_VENDORS_EDITOR"]:
        template_name = 'vendors/form-editor-markdown.html'

    return render(request, template_name, context)
