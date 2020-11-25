import sweetify

from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses import settings
from nolsatu_courses.apps.decorators import superuser_required
from nolsatu_courses.apps.vouchers.models import Voucher
from .forms import FormVoucher


@superuser_required
def index(request):
    vouchers = Voucher.objects.all()

    context = {
        'menu_active': 'vouchers',
        'title': _('Daftar Kupon'),
        'vouchers': vouchers,
    }
    return render(request, 'backoffice/vouchers/index.html', context)


@superuser_required
def detail(request, id):
    voucher = get_object_or_404(Voucher, id=id)

    context = {
        'menu_active': 'vouchers',
        'title': _('Detail Kupon'),
        'voucher': voucher,
    }
    return render(request, 'backoffice/vouchers/detail.html', context)


@superuser_required
@transaction.atomic
def delete(request, id):
    voucher = get_object_or_404(Voucher, id=id)
    voucher.delete()
    sweetify.success(request, 'Berhasil hapus voucher', icon='success', button='OK')
    return redirect('backoffice:vouchers:index')


@superuser_required
@transaction.atomic
def add(request):
    form = FormVoucher(data=request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save()
        sweetify.success(request, _(f"Berhasil tambah voucher {post.code}"), button='OK', icon='success')
        return redirect('backoffice:vouchers:index')

    context = {
        'menu_active': 'vouchers',
        'title': _('Tambah Kupon'),
        'form': form,
        'title_submit': 'Simpan'
    }

    template = 'backoffice/form-editor.html'
    if settings.FEATURE["MARKDOWN_BACKOFFICE_EDITOR"]:
        template = 'backoffice/form-editor-markdown.html'

    return render(request, template, context)
