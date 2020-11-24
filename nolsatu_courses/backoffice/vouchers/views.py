from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.decorators import superuser_required
from nolsatu_courses.apps.vouchers.models import Voucher


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
