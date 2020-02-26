from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.api.courses.serializers import (
    CourseSerializer, CourseDetailMergeSerializer, CourseEnrollSerializer, CoursePreviewListSerializer,
    ModulePreviewSerializer, SectionPreviewSerializer, ModuleDetailSerializer
)
from nolsatu_courses.api.serializers import MessageSuccesSerializer, ErrorMessageSerializer
from nolsatu_courses.api.authentications import UserAuthAPIView
from nolsatu_courses.api.response import ErrorResponse
from nolsatu_courses.apps.courses.models import Courses, Module, Section
from nolsatu_courses.apps import utils
from nolsatu_courses.website.modules.views import get_pagination


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
        responses={
            200: MessageSuccesSerializer(),
            400: ErrorMessageSerializer()
        }
    )
    def get(self, request, id):
        course = get_object_or_404(Courses, id=id)

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


class CoursePreviewListView(APIView):

    @swagger_auto_schema(tags=['Courses'], operation_description="Get Course Preview List", responses={
        200: CoursePreviewListSerializer()
    })
    def get(self, request, id):
        course = get_object_or_404(Courses, id=id)
        serializer = CoursePreviewListSerializer(course)
        return Response(serializer.data)


class ModulePreviewView(APIView):

    @swagger_auto_schema(tags=['Courses'], operation_description="Get Module Preview", responses={
        200: ModulePreviewSerializer()
    })
    def get(self, request, id):
        module = get_object_or_404(Module, id=id)
        serializer = ModulePreviewSerializer(module)
        return Response(serializer.data)


class SectionPreviewView(APIView):

    @swagger_auto_schema(tags=['Courses'], operation_description="Get Section Preview", responses={
        200: SectionPreviewSerializer()
    })
    def get(self, request, id):
        section = get_object_or_404(Section, id=id)
        serializer = SectionPreviewSerializer(section)
        return Response(serializer.data)


class ModuleDetailView(UserAuthAPIView):

    @swagger_auto_schema(tags=['Courses'], operation_description="Get Module Detail", responses={
        200: ModuleDetailSerializer()
    })
    def get(self, request, id):
        module = get_object_or_404(Module, id=id)
        pagination = get_pagination(request, module)

        # handle ketika user belum mengumpulkan tugas pada sesi sebelumnya
        # jika page_type adalah section dan section memiliki tugas
        if pagination['prev_type'] == 'section' and pagination['prev'].is_task:
            if not pagination['prev'].collect_task.all():
                return ErrorResponse(
                    error_message=_(f"Kamu harus mengumpulkan tugas pada sesi {pagination['prev'].title}"))

        # save activities user to module
        if module.has_enrolled(request.user):
            module.activities_module.get_or_create(
                user=request.user, course=module.course)

        data = {
            'module': module,
            'pagination': {
                'next_slug': pagination['next'].slug if pagination['next'] else "",
                'prev_slug': pagination['prev'].slug if pagination['prev'] else "",
                'next_type': pagination['next_type'],
                'prev_type': pagination['prev_type']
            }
        }
        return Response(ModuleDetailSerializer(data).data)
