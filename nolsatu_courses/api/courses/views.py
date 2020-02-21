from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from nolsatu_courses.api.courses.serializers import CourseSerializer, CourseDetailSerializer
from nolsatu_courses.apps.courses.models import Courses


class CourseListView(APIView):

    @swagger_auto_schema(tags=['Courses'], operation_description="Get Course List", responses={
        200: CourseSerializer(many=True)
    })
    def get(self, request):
        courses = Courses.objects.filter(is_visible=True).all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)


class CourseDetailView(APIView):

    @swagger_auto_schema(tags=['Courses'], operation_description="Get Course Detail", responses={
        200: CourseDetailSerializer(many=True)
    })
    def get(self, request, id):
        course = get_object_or_404(Courses, id=id)
        serializer = CourseDetailSerializer(course)
        return Response(serializer.data)
