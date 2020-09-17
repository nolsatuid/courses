from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum, F
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.products.models import Cart, Product, Order, OrderItem


@login_required
def cart(request):
    carts = Cart.objects.filter(user=request.user)

    context = {
        'title': _('Keranjang'),
        'carts': carts.order_by('-id'),
        'total': carts.filter(is_select=True).annotate(final_price=F('product__price') - F('product__discount')
                                                       ).aggregate(total_price=Sum('final_price'))
    }

    if not context['total']['total_price']:
        context['total'] = {'total_price': '-'}

    return render(request, 'website/user/cart.html', context)


@login_required
@transaction.atomic
def cart_delete(request, cart_id):
    cart = get_object_or_404(Cart, id=cart_id, user=request.user)
    data = dict()
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
    try:
        Cart.objects.get(product=pick_product, user=request.user)
        data['message'] = _('Gagal Menambahkan, Kursus Sudah Ada Di Keranjang!')
    except Cart.DoesNotExist:
        Cart(product=pick_product, user=request.user).save()

    return JsonResponse(data, status=200)


@login_required
def choose_item(request):
    data = dict()
    if request.method == 'POST':
        if request.POST.get('change_item[item]'):
            Cart.objects.filter(id=request.POST.get('change_item[item]')).update(
                is_select=request.POST.get('change_item[selected]'))

        carts = Cart.objects.filter(user=request.user, is_select=True)
        data['total'] = carts.annotate(final_price=F('product__price') - F('product__discount')
                                       ).aggregate(price=Sum('final_price'))
        if not data['total']['price']:
            data['total'] = {'price': '-'}
    return JsonResponse(data, status=200)


@login_required
@transaction.atomic
def checkout(request):
    carts = Cart.objects.filter(user=request.user, is_select=True)
    total = carts.annotate(final_price=F('product__price') - F('product__discount')
                           ).aggregate(total_price=Sum('final_price'))
    context = {
        'title': _('Checkout'),
        'carts': carts,
        'total': total
    }
    return render(request, 'website/carts/checkout.html', context)


@login_required
@transaction.atomic
def payment(request):
    """
    - create Order
    - create OrderItem
    - delete Cart yang is_select = True
    - request to bpay

    if request bpay valid, redirect to bpay snap page
    if request invalid, redirect to order detail.
    """
    carts = Cart.objects.filter(user=request.user, is_select=True)
    total = carts.annotate(final_price=F('product__price') - F('product__discount')
                           ).aggregate(total_price=Sum('final_price'))

    tax = total['total_price'] / 100 * settings.TAX_VALUE
    discount = 0
    order = Order(
        user=request.user,
        number=timezone.now().timestamp(),
        tax=tax,
        discount=discount,
        grand_total=total['total_price'] + tax - discount,
    )
    order.save()

    order_item = [OrderItem(
        order=order,
        product=item.product,
        price=item.product.price - item.product.discount,
        name=item.product.course.title,
    ) for item in carts]

    OrderItem.objects.bulk_create(order_item)
    carts.delete()

    return redirect('website:index')
