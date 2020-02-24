from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from nolsatu_courses.api.courses.serializers import (
    CourseSerializer, CourseDetailSerializer, CourseDetailMergeSerializer,
    CourseEnrollSerializer
)
from nolsatu_courses.api.authentications import UserAuthAPIView
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
        200: CourseDetailMergeSerializer()
    })
    def get(self, request, id):
        course = get_object_or_404(Courses, id=id)
        data = {
            'course': course,
            'batch': course.get_last_batch(),
            'has_enrolled': course.has_enrolled(request.user),
            'enroll': course.get_enroll(request.user)
        }
        serializer = CourseDetailMergeSerializer(data)
        return Response(serializer.data)


class CourseEnrollDetailView(UserAuthAPIView):

    @swagger_auto_schema(tags=['Courses'], operation_description="To Enroll Course", responses={
        200: CourseEnrollSerializer()
    })
    def get(self, request, id):
        course = get_object_or_404(Courses, id=id)
        data = {
            'has_enrolled': course.has_enrolled(request.user),
            'enroll': course.get_enroll(request.user)
        }
        serializer = CourseEnrollSerializer(data)
        return Response(serializer.data)
