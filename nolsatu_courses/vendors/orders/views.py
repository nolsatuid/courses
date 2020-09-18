from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from nolsatu_courses.apps.decorators import vendor_member_required
from nolsatu_courses.apps.products.models import OrderItem


@vendor_member_required
def index(request):
    order_item = OrderItem.objects.filter(
            product__course__vendor__users__email=request.user.email)

    context = {
        'menu_active': 'order',
        'title': _('Daftar Order'),
        'order_item': order_item,
        'sidebar': True
    }
    return render(request, 'vendors/orders/index.html', context)
