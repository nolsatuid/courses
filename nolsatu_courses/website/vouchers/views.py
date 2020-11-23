from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _


def index(request):
    context = {
        'title': _('Daftar Kupon'),
        # 'user_page': False
    }
    return render(request, 'website/vouchers/index.html', context)
