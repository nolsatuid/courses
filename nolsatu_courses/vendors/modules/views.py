from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404

from nolsatu_courses.apps.courses.models import Courses, Module
from nolsatu_courses.backoffice.modules.forms import FormModule


@staff_member_required
def index(request, id):
    course = get_object_or_404(Courses, id=id, vendor__users__email=request.user.email)
    context = {
        'menu_active': 'course',
        'title': _('Daftar Modul'),
        'modules': course.modules.all(),
        'course': course,
        'sidebar': True
    }
    return render(request, 'vendors/modules/index.html', context)


@staff_member_required
def create(request, id):
    course = get_object_or_404(Courses, id=id, vendor__users__email=request.user.email)
    form = FormModule(data=request.POST or None, files=request.FILES or None)
    if form.is_valid():
        module = form.save(commit=False)
        module.course = course
        module.save()
        messages.success(request, _(f"Berhasil tambah modul {module.title}"))
        return redirect('vendors:modules:index', id=id)

    context = {
        'menu_active': 'course',
        'title': _('Tambah Modul'),
        'form': form,
        'title_submit': 'Simpan'
    }

    template_name = 'vendors/form-editor.html'
    if settings.FEATURE["MARKDOWN_VENDORS_EDITOR"]:
        template_name = 'vendors/form-editor-markdown.html'

    return render(request, template_name, context)
