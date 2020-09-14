from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum, F
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.products.models import Cart, Product


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


@login_required
@transaction.atomic
def add_item(request, product_id):
    pick_product = get_object_or_404(Product, id=product_id)
    data = dict()
    if request.method == 'POST':
        try:
            item_in_cart = Cart.objects.get(product=pick_product, user=request.user)
            data['message'] = _('Gagal Menambahkan, Kursus Sudah Ada Di Keranjang!')
        except item_in_cart.DoesNotExist:
            Cart(product=pick_product, user=request.user).save()

    return JsonResponse(data, status=200)
