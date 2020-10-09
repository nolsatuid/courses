from drf_yasg.utils import swagger_auto_schema
from requests import Response
from rest_framework import status

from rest_framework.response import Response

from nolsatu_courses.api.authentications import UserAuthAPIView
from nolsatu_courses.apps.products.models import Order

from .serializers import OrderSerializer


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
