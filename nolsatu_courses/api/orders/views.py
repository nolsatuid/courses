from drf_yasg.utils import swagger_auto_schema
from requests import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404

from rest_framework.response import Response

from nolsatu_courses.api.authentications import UserAuthAPIView
from nolsatu_courses.apps.products.models import Order

from .serializers import OrderSerializer, OrderAllFieldsSerializer, OrderItemSerializer


class OrderListView(UserAuthAPIView):
    @swagger_auto_schema(tags=['Orders'], operation_description="My Orders",
                         responses={status.HTTP_200_OK: OrderSerializer(many=True)}, )
    def get(self, request):
        orders = Order.objects.filter(user=self.request.user)
        serializer = OrderSerializer(orders, many=True)
        resp = {
            "orders": serializer.data,
        }
        return Response(resp)


class DetailOrderView(UserAuthAPIView):
    @swagger_auto_schema(tags=['Orders'], operation_description="My Orders Detail",
                         responses={status.HTTP_200_OK: ""}, )
    def get(self, request, id):
        order = get_object_or_404(Order, user=self.request.user, id=id)
        order_items = order.orders.all()

        serializer_order = OrderAllFieldsSerializer(order)
        serializer_order_items = OrderItemSerializer(order_items, many=True)

        data = {"order": serializer_order.data,
                "order_items": serializer_order_items.data
                }

        return Response(data)
