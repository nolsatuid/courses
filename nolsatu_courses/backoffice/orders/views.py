from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from nolsatu_courses.apps.decorators import superuser_required
from nolsatu_courses.apps.products.models import Order, OrderItem


@superuser_required
def index(request):
    context = {
        'menu_active': 'order',
        'title': _('Daftar Order'),
        'orders': Order.objects.select_related('user'),
        'sidebar': True
    }
    return render(request, 'backoffice/orders/index.html', context)


@superuser_required
def details(request, id):
    order = get_object_or_404(Order, id=id)
    order_items = order.orders.all()

    context = {
        'menu_active': 'order',
        'title': 'Detail Order',
        'order': order,
        'order_items': order_items
    }
    return render(request, 'backoffice/orders/detail.html', context)
