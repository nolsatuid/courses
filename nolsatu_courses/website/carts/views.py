import logging
import requests

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from nolsatu_courses.apps.decorators import ajax_login_required
from django.db import transaction
from django.db.models import Sum, F
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from fortuna_client.exception import FortunaException

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


@ajax_login_required
@transaction.atomic
def add_item(request, product_id):
    pick_product = get_object_or_404(Product, id=product_id)
    data = dict()
    status_check = [Order.STATUS.created, Order.STATUS.pending, Order.STATUS.success]
    product_in_order_item = pick_product.orderitem_set.first() if pick_product.orderitem_set.first() else False

    try:
        if pick_product.course.has_enrolled(user=request.user):
            data['message'] = _('Gagal Menambahkan, Anda Telah terdaftar di dalam kursus!')
        elif product_in_order_item and product_in_order_item.order.status in status_check:
            data['message'] = _('Gagal Menambahkan, Anda Telah Melakukan Pembelian Pada Kursus ini!')
        else:
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


@ajax_login_required
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

    data = dict()
    status_check = [Order.STATUS.created, Order.STATUS.pending, Order.STATUS.success]

    for item in carts:
        product_in_order_item = item.product.orderitem_set.first() if item.product.orderitem_set.first() else False

        if item.product.course.has_enrolled(user=request.user):
            data['message'] = _(f'Gagal Menambahkan, Anda Telah Terdaftar Di Dalam Kursus {item.product.course.title}!')
            data['redirect_url'] = reverse('website:courses:details', args=(item.product.course.id, ))
            return JsonResponse(data, status=200)
        elif product_in_order_item and product_in_order_item.order.status in status_check:
            data['message'] = _(f'Gagal Menambahkan, Anda Telah Melakukan Pembelian Pada Kursus '
                                f'{item.product.course.title}!')
            return JsonResponse(data, status=200)

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

    # Request BPay
    try:
        remote_transaction = order.create_transaction()
        if remote_transaction:
            data['redirect_url'] = remote_transaction.snap_redirect_url
            return JsonResponse(data, status=200)
    except FortunaException:
        logging.exception("Failed to create transaction")
        return JsonResponse(data, status=200)
    except requests.ConnectionError:
        data['message'] = 'Server Sedang Mengalami Masalah'
        logging.exception("Failed to create transaction")
        return JsonResponse(data, status=200)

    data['redirect_url'] = reverse('website:orders:details', args=(order.id,))
    return JsonResponse(data, status=200)
