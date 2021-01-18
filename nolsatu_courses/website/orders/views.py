import requests
import logging

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from fortuna_client.exception import FortunaException

from nolsatu_courses.apps.decorators import ajax_login_required
from nolsatu_courses.apps.products.models import Cart, Product, Order, OrderItem


@login_required
def index(request):
    context = {
        'title': _('Daftar Order'),
        'orders': Order.objects.select_related('user').filter(user=request.user),
    }

    return render(request, 'website/orders/index.html', context)


@login_required
def details(request, order_id):
    order = get_object_or_404(Order, user=request.user, id=order_id)
    order_items = order.orders.all()

    context = dict()

    # read status
    try:
        billing = order.get_transaction()

        if not billing:
            billing = order.create_transaction()

        if billing:
            context['url_finishing_payment'] = billing.snap_redirect_url
            context['exp_payment'] = billing.expired_at
    except FortunaException:
        context['message'] = 'Server Sedang Mengalami Masalah'
        logging.exception("Failed to create transaction")
    except requests.ConnectionError:
        context['message'] = 'Server Sedang Mengalami Masalah'
        logging.exception("Failed to create transaction")

    context['title'] = 'Detail Order'
    context['order'] = order
    context['order_items'] = order_items

    return render(request, 'website/orders/detail.html', context)


@ajax_login_required
@login_required
@transaction.atomic
def cancel(request, order_id):
    order = get_object_or_404(Order, user=request.user, id=order_id)
    context = dict()
    # canceling transaction
    try:
        order.cancel_transaction()
    except FortunaException:
        logging.exception("Failed to cancel transaction")
        context['message'] = 'Server Sedang Mengalami Masalah'
    except requests.ConnectionError:
        logging.exception("Failed to cancel transaction, Connection Error")
        context['message'] = 'Koneksi Jaringan Error'

    return JsonResponse(context, status=200)
