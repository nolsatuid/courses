from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

from nolsatu_courses.api.vendors.serializers import (
    VendorListSerializer,
)
from nolsatu_courses.apps.vendors.models import Vendor
from nolsatu_courses.api.authentications import InternalAPIView


class VendorListView(InternalAPIView):

    @swagger_auto_schema(tags=['Vendors'], operation_description="Get Vendor List", responses={
        200: VendorListSerializer(many=True)
    })
    def get(self, request):
        vendors = Vendor.objects.all()

        serializer = VendorListSerializer(vendors, many=True)
        return Response(serializer.data)
