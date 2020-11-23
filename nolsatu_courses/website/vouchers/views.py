from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.vouchers.models import UserVoucher


def index(request):
    vouchers = UserVoucher.objects.filter(user=request.user)
    context = {
        'title': _('Daftar Kupon'),
        'vouchers': vouchers
    }
    return render(request, 'website/vouchers/index.html', context)


