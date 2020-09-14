from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum, F
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.products.models import Cart


@login_required
def cart(request):
    carts = Cart.objects.filter(user=request.user)
    context = {
        'title': _('Keranjang'),
        'carts': carts,
        'total': carts.annotate(final_price=F('product__price') - F('product__discount')
                                ).aggregate(total_price=Sum('final_price'))
    }
    return render(request, 'website/user/cart.html', context)


@login_required
@transaction.atomic
def cart_delete(request, cart_id):
    cart = get_object_or_404(Cart, id=cart_id, user=request.user)
    data = dict()
    if request.method == 'POST':
        cart.delete()
        carts = Cart.objects.filter(user=request.user)
        data['total'] = carts.annotate(final_price=F('product__price') - F('product__discount')
                                       ).aggregate(price=Sum('final_price'))
    return JsonResponse(data, status=200)
