import urllib.parse

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Sum, F
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.courses.models import Courses
from nolsatu_courses.apps.products.models import Cart


def index(request):
    if request.user and request.user.is_superuser:
        courses = Courses.objects.all()
    else:
        courses = Courses.objects.filter(
            is_visible=True, status=Courses.STATUS.publish
        )

    context = {
        'title': _('Daftar Materi'),
        'courses': [{
            'course': course,
            'has_enrolled': course.has_enrolled(request.user)
        } for course in courses],
        'user_page': False
    }
    return render(request, 'website/index.html', context)


@login_required()
def search(request):
    search_query = request.GET.get("q", "")

    context = {
        'title': _(f'Hasil Pencarian untuk "{search_query}"'),
        'search_query': search_query,
        'courses': Courses.objects.filter(Q(title__contains=search_query) | Q(description__contains=search_query)),
        'progress_bar': False
    }
    return render(request, 'website/index.html', context)


@login_required()
def logout(request):
    params = urllib.parse.urlencode({
        'next': settings.LOGOUT_REDIRECT_URL
    })
    return redirect(f'{settings.LOGOUT_URL}?{params}')


@login_required
def login(request):
    return redirect("website:index")


@login_required
def test_login(request):
    context = {
        'title': _('Kursus'),
        'courses': Courses.objects.all()
    }
    return render(request, 'website/index.html', context)


def error_404(request):
    return render(request, '404.html', {})


def error_500(request):
    return render(request, '500.html', {})


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
