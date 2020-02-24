from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.api.courses.serializers import (
    CourseSerializer, CourseDetailMergeSerializer, CourseEnrollSerializer
)
from nolsatu_courses.api.authentications import UserAuthAPIView
from nolsatu_courses.api.response import ErrorResponse
from nolsatu_courses.apps.courses.models import Courses
from nolsatu_courses.apps import utils


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

    @swagger_auto_schema(tags=['Courses'], operation_description="Enroll Detail", responses={
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


class EnrollCourseView(UserAuthAPIView):

    @swagger_auto_schema(
        tags=['Courses'], operation_description="To Enroll Course",
        responses={200: "{message: 'Kamu berhasil terdaftar pada kelas .....'}"}
    )
    def get(self, request, slug):
        course = get_object_or_404(Courses, slug=slug)

        if course.has_enrolled(request.user):
            return ErrorResponse(error_message=_(f'Kamu sudah terdaftar di kelas {course.title}'))

        if not course.get_last_batch():
            return ErrorResponse(error_message=_(f'Kelas {course.title} belum membuka pendaftaran'))

        if course.is_started():
            return ErrorResponse(error_message=_(f'Gagal mendaftar, kelas {course.title} sudah dimulai'))

        course.enrolled.create(course=course, user=request.user, batch=course.batchs.last())
        utils.send_notification(
            request.user,
            f'Kamu berhasil mendaftar di kelas {course.title}',
            f'Saat ini kamu sudah berhasil mendaftar pada kelas {course.title}. Tunggu info selanjutnya ya.'
        )
        return Response({'message': _(f'Kamu berhasil terdaftar pada kelas {course.title}')})
