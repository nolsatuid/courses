from django.db import transaction, DatabaseError
from django.db.models import Sum, F
from django.utils.translation import ugettext_lazy as _

from drf_yasg.utils import swagger_auto_schema
from requests import Response
from rest_framework import status

from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from nolsatu_courses.api.authentications import UserAuthAPIView
from nolsatu_courses.api.response import ErrorResponse
from nolsatu_courses.apps.products.models import Product, Order, Cart

from .serializers import AddCartSerializer, CartIDSerializer, CartSerializer, CartCountSerializer, FullCartSerializer


class AddToCartView(UserAuthAPIView):
    @swagger_auto_schema(tags=['Carts'], operation_description="Add to My Carts",
                         responses={status.HTTP_200_OK: AddCartSerializer()},
                         request_body=AddCartSerializer)
    def post(self, request):
        data = request.data

        serializer = AddCartSerializer(data=data)

        if serializer.is_valid():
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
        else:
            return ErrorResponse(error_message=_('Gagal Menambahkan Kursus ke Keranjang'))


class DeleteItemCartView(UserAuthAPIView):
    @swagger_auto_schema(tags=['Carts'], operation_description="Delete Item in Carts",
                         responses={status.HTTP_200_OK: CartIDSerializer()},
                         request_body=CartIDSerializer)
    def post(self, request):
        data = request.data
        serializer = CartIDSerializer(data=data)

        if serializer.is_valid():
            validated_data = serializer.validated_data

            carts = Cart.objects.filter(id__in=validated_data['cart_ids'], user=self.request.user)

            if not carts:
                return Response({'message': _('Kursus tidak ada dalam keranjang')})

            try:
                with transaction.atomic():
                    carts.delete()
            except DatabaseError:
                return Response({'message': _('Gagal menghapus kursus dalam keranjang')})

            return Response({'message': _('Berhasil menghapus kursus pada keranjang')})


class CartListView(UserAuthAPIView):
    @swagger_auto_schema(tags=['Carts'], operation_description="My Carts",
                         responses={status.HTTP_200_OK: FullCartSerializer()}, )
    def get(self, request):
        carts = Cart.objects.filter(user=self.request.user)

        total = carts.annotate(final_price=F('product__price') - F('product__discount')
                               ).aggregate(total_price=Sum('final_price'))

        carts = [
            {
                "id": c.id,
                "product": {
                    'id': c.product.id,
                    'price': c.product.price,
                    'code': c.product.code,
                    'discount_type': c.product.discount_type,
                    'discount_value': c.product.discount_value,
                    'discount': c.product.discount,
                    'course': {'id': c.product.course.id, 'title': c.product.course.title},
                }
            } for c in carts
        ]

        data = {
            "carts": carts,
            "total": total['total_price'] or 0
        }

        serializer = FullCartSerializer(data=data)

        if serializer.is_valid():
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class CheckoutView(UserAuthAPIView):
    @swagger_auto_schema(tags=['Carts'], operation_description="Checkout",
                         responses={status.HTTP_200_OK: CartSerializer(many=True)})
    def get(self, request):
        carts = Cart.objects.filter(user=self.request.user, is_select=True)

        total = carts.annotate(final_price=F('product__price') - F('product__discount')
                               ).aggregate(total_price=Sum('final_price'))

        data = [{"id": c.id,
                 "product": {'id': c.product.id,
                             'price': c.product.price,
                             'code': c.product.code,
                             'discount_type': c.product.discount_type,
                             'discount_value': c.product.discount_value,
                             'discount': c.product.discount,
                             'course': {'id': c.product.course.id, 'title': c.product.course.title},
                             }
                 } for c in carts]

        serializer = CartSerializer(data=data, many=True)

        if serializer.is_valid(raise_exception=True):
            resp = {
                "carts": serializer.data,
                "total": total['total_price']
            }
            return Response(resp)
        else:
            return Response(serializer.errors)


class CartCountView(UserAuthAPIView):
    @swagger_auto_schema(
        tags=['Carts'],
        operation_description="Cart Count",
        responses={
            status.HTTP_200_OK: CartCountSerializer()
        }
    )
    def get(self, request):
        data = {
            "count": Cart.objects.filter(user=self.request.user).count(),
        }

        serializer = CartCountSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
