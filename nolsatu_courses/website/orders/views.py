from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _

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
    order = get_object_or_404(Order, id=order_id)
    order_items = order.orders.all()

    context = {
        'title': 'Detail Order',
        'order': order,
        'order_items': order_items
    }
    return render(request, 'website/orders/detail.html', context)
