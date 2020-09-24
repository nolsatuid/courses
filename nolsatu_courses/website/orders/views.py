import requests
import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from fortuna_client.exception import FortunaException

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
        billing = None

        if order.status == Order.STATUS.created:
            billing = order.create_transaction()
        elif order.status == Order.STATUS.pending:
            billing = order.get_transaction()

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
