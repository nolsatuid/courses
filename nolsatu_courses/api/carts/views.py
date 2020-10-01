from django.utils.translation import ugettext_lazy as _

from drf_yasg.utils import swagger_auto_schema
from requests import Response
from rest_framework import status

from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from nolsatu_courses.api.authentications import UserAuthAPIView
from nolsatu_courses.api.response import ErrorResponse
from nolsatu_courses.apps.products.models import Product, Order, Cart

from .serializers import AddCartSerializer


# Here add your api view

class AddToCartView(UserAuthAPIView):
    @swagger_auto_schema(tags=['Carts'], operation_description="Add to My Carts",
                         responses={status.HTTP_200_OK: AddCartSerializer()},
                         request_body=AddCartSerializer)
    def post(self, request):
        data = request.data

        if not data.get('product_id'):
            return ErrorResponse(error_message=_('Gagal Menambahkan Kursus ke Keranjang'))

        status_check = [Order.STATUS.created, Order.STATUS.pending, Order.STATUS.success]

        pick_product = get_object_or_404(Product, id=data.get('product_id'))
        user_order_item = pick_product.orderitem_set.filter(order__user=self.request.user).first()

        try:
            if pick_product.course.has_enrolled(user=self.request.user):
                return ErrorResponse(error_message=_('Gagal Menambahkan, Anda Telah terdaftar '
                                                     'di dalam kursus!'))
            elif user_order_item and user_order_item.order.status in status_check:
                return ErrorResponse(error_message=_('Gagal Menambahkan, Anda Telah Melakukan '
                                                     'Pembelian Pada Kursus ini!'))
            else:
                Cart.objects.get(product=pick_product, user=self.request.user)
                return ErrorResponse(error_message=_('Gagal Menambahkan, Kursus Sudah Ada '
                                                     'di Keranjang!'))
        except Cart.DoesNotExist:
            Cart(product=pick_product, user=self.request.user).save()

        return Response({'message': _('Berhasil Menambahkan Kursus ke Keranjang')})
