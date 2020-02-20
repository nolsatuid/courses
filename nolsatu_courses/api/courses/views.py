from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

from nolsatu_courses.api.authentications import UserAuthAPIView
from nolsatu_courses.api.courses.serializers import CourseSerializer
from nolsatu_courses.apps.courses.models import Courses


class CourseListView(UserAuthAPIView):
    @swagger_auto_schema(tags=['Courses'], operation_description="Get Course List", responses={
        200: CourseSerializer(many=True)
    })
    def get(self, request):
        courses = Courses.objects.filter(is_visible=True).all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)