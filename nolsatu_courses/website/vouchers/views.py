from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.vouchers.models import UserVoucher, Voucher


def index(request):
    vouchers = UserVoucher.objects.filter(user=request.user)
    context = {
        'title': _('Daftar Kupon'),
        'vouchers': vouchers
    }
    return render(request, 'website/vouchers/index.html', context)


def detail(request, id):
    vouchers = get_object_or_404(Voucher, id=id)
    context = {
        'voucher': vouchers
    }
    return render(request, 'website/vouchers/detail.html', context)
