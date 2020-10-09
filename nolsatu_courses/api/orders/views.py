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

        data = [{"id": x.id,
                 "number": x.number,
                 "status": x.get_status_display(),
                 "created_at": x.created_at,
                 } for x in orders]

        serializer = OrderSerializer(data=data, many=True)

        if serializer.is_valid(raise_exception=True):
            resp = {
                "orders": serializer.data,
            }
            return Response(resp)
        else:
            return Response(serializer.errors)
