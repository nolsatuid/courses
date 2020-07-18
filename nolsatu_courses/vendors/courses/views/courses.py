from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.courses.models import Courses
from nolsatu_courses.apps.vendors.models import Vendor
from nolsatu_courses.backoffice.courses.forms import FormCourses


@staff_member_required
def get_list_courses(request):
    context = {
        'courses': Courses.objects.filter(vendor__users__email=request.user.email),
        'menu_active': 'course',
        'title': _('Daftar Kursus'),
        'sidebar': True
    }
    return render(request, 'vendors/courses/courses-list.html', context)


@staff_member_required
def get_details_courses(request, courses_id):
    course = get_object_or_404(Courses, id=courses_id, vendor__users__email=request.user.email)
    context = {
        'menu_active': 'course',
        'title': 'Detail Kursus',
        'course': course,
    }
    return render(request, 'vendors/courses/course-detail.html', context)


@staff_member_required
def create_course(request):
    template_name = 'vendors/courses/course-create.html'

    form = FormCourses(data=request.POST or None, files=request.FILES or None)
    vendor = Vendor.objects.filter(users__email=request.user.email).first()
    author = User.objects.filter(email=request.user.email).first()

    if form.is_valid():
        with transaction.atomic():
            course = form.save()
        messages.success(request, _(f"Berhasil tambah kursus {course.title}"))
        return redirect('vendors:courses:index')

    context = {
        'menu_active': 'course',
        'title': _('Tambah Kursus'),
        'form': form,
        'author': author,
        'vendor': vendor,
        'title_submit': 'Simpan'
    }

    if settings.FEATURE["MARKDOWN_BACKOFFICE_EDITOR"]:
        template_name = 'backoffice/form-editor-markdown.html'

    return render(request, template_name, context)
