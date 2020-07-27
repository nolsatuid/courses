from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from nolsatu_courses.api.courses.serializers import (
    CourseSerializer, CourseDetailMergeSerializer, CourseEnrollSerializer, CoursePreviewListSerializer,
    ModulePreviewSerializer, SectionPreviewSerializer, ModuleDetailSerializer, SectionDetailSerializer,
    CollectTaskSerializer, CourseTrackingListSerializer
)
from nolsatu_courses.api.serializers import MessageSuccesSerializer, ErrorMessageSerializer
from nolsatu_courses.api.authentications import UserAuthAPIView
from nolsatu_courses.api.response import ErrorResponse
from nolsatu_courses.apps.courses.models import Courses, Module, Section, Enrollment, CollectTask
from nolsatu_courses.apps import utils
from nolsatu_courses.website.modules.views import get_pagination as get_pagination_module
from nolsatu_courses.website.sections.views import get_pagination as get_pagination_section


class CourseListView(APIView):

    @swagger_auto_schema(tags=['Courses'], operation_description="Get Course List", responses={
        200: CourseSerializer(many=True)
    })
    def get(self, request):
        courses = Courses.objects.filter(is_visible=True, status=Courses.STATUS.publish).all()

        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)


class MyCourseListView(UserAuthAPIView):
    @swagger_auto_schema(tags=['Courses'], operation_description="Get My Course List", responses={
        200: CourseSerializer(many=True)
    })
    def get(self, request):
        courses = Courses.objects.filter(enrolled__user=request.user)
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


class CoursePreviewListView(APIView):

    @swagger_auto_schema(tags=['Courses'], operation_description="Get Course Preview List", responses={
        200: CoursePreviewListSerializer()
    })
    def get(self, request, id):
        course = get_object_or_404(Courses, id=id)
        serializer = CoursePreviewListSerializer(course)
        return Response(serializer.data)


class ModulePreviewView(APIView):

    @swagger_auto_schema(tags=['Module'], operation_description="Get Module Preview", responses={
        200: ModulePreviewSerializer()
    })
    def get(self, request, id):
        module = get_object_or_404(Module, id=id)
        serializer = ModulePreviewSerializer(module)
        return Response(serializer.data)


class ModuleDetailView(UserAuthAPIView):

    @swagger_auto_schema(tags=['Module'], operation_description="Get Module Detail", responses={
        200: ModuleDetailSerializer()
    })
    def get(self, request, id):
        module = get_object_or_404(Module, id=id)
        pagination = get_pagination_module(request, module)

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
            'is_complete_tasks': module.course.is_complete_tasks(request.user),
            'module': module,
            'pagination': {
                'next_id': pagination['next'].id if pagination['next'] else None,
                'next_type': pagination['next_type'] if pagination['next'] else None,
                'prev_id': pagination['prev'].id if pagination['prev'] else None,
                'prev_type': pagination['prev_type'] if pagination['prev'] else None,
            }
        }
        return Response(ModuleDetailSerializer(data).data)


class SectionPreviewView(APIView):

    @swagger_auto_schema(tags=['Section'], operation_description="Get Section Preview", responses={
        200: SectionPreviewSerializer()
    })
    def get(self, request, id):
        section = get_object_or_404(Section, id=id)
        serializer = SectionPreviewSerializer(section)
        return Response(serializer.data)


class SectionDetailView(UserAuthAPIView):

    @swagger_auto_schema(tags=['Section'], operation_description="Get Section Detail", responses={
        200: SectionDetailSerializer()
    })
    def get(self, request, id):
        section = get_object_or_404(Section, id=id)
        pagination = get_pagination_section(request, section)

        # handle ketika user belum mengumpulkan tugas pada sesi sebelumnya
        # jika page_type adalah section dan section memiliki tugas
        if pagination['prev_type'] == 'section' and pagination['prev'].is_task:
            if not pagination['prev'].collect_task.all():
                return ErrorResponse(
                    error_message=_(f"Kamu harus mengumpulkan tugas pada sesi {pagination['prev'].title}"))

        # save activities user to module
        if section.has_enrolled(request.user):
            section.activities_section.get_or_create(
                user=request.user, course=section.module.course)

        data = {
            'is_complete_tasks': section.module.course.is_complete_tasks(request.user),
            'section': section,
            'pagination': {
                'next_id': pagination['next'].id if pagination['next'] else None,
                'next_type': pagination['next_type'] if pagination['next'] else None,
                'prev_id': pagination['prev'].id if pagination['prev'] else None,
                'prev_type': pagination['prev_type'] if pagination['prev'] else None
            }
        }
        return Response(SectionDetailSerializer(data).data)


class CollectTaskView(UserAuthAPIView):

    @swagger_auto_schema(tags=['Enrolment'], operation_description="Collect Task", responses={
        200: CollectTaskSerializer()
    })
    def get(self, request, section_id):
        task = CollectTask.objects.filter(section_id=section_id, user=request.user).first()
        data = {
            'message': '',
            'status': 0
        }
        if task:
            if task.status == CollectTask.STATUS.review:
                data['message'] = f"Yey, sekarang <a href='{settings.HOST}{task.file.file.url}'><strong>tugas kamu</strong> \
                    </a> sedang <span class='badge badge-secondary' style='font-size:100%;'>diperiksa</span>"
                if task.note:
                    data[
                        'message'] += f"<br><br>Wah ada catatan nih dari instruktur kamu: <br><strong>{task.note}</strong>"
                data['status'] = CollectTask.STATUS.review
            elif task.status == CollectTask.STATUS.repeat:
                data[
                    'message'] = f"Yah, kamu harus <strong>mengulang</strong> pada <a href='{settings.HOST}{task.file.file.url}'> \
                    <strong>tugas ini</strong></a>. Ayo kirim ulang tugas yang sudah diperbaiki!"
                if task.note:
                    data['message'] += f"<br><br>Ini nih catatan dari instruktur kamu: <br><strong>{task.note}</strong>"
                data['status'] = CollectTask.STATUS.repeat
            elif task.status == CollectTask.STATUS.graduated:
                data['message'] = f"Yey, kamu <span class='badge badge-light' style='font-size:100%;'>lulus</span> pada \
                    <a href='{settings.HOST}{task.file.file.url}'><strong> tugas ini</strong></a>. Semoga sukses di tugas-tugas selanjutnya."
                if task.note:
                    data[
                        'message'] += f"<br><br>Wah ada catatan nih dari instruktur kamu: <br><strong>{task.note}</strong>"
                data['status'] = CollectTask.STATUS.graduated

        return Response(CollectTaskSerializer(data).data)


class CourseEnrollDetailView(UserAuthAPIView):

    @swagger_auto_schema(tags=['Enrolment'], operation_description="Enroll Detail", responses={
        200: CourseEnrollSerializer()
    })
    def get(self, request, id):
        course = get_object_or_404(Courses, id=id)
        data = {
            'can_register': course.can_register(request.user),
            'has_enrolled': course.has_enrolled(request.user),
            'enroll': course.get_enroll(request.user)
        }
        serializer = CourseEnrollSerializer(data)
        return Response(serializer.data)


class EnrollCourseView(UserAuthAPIView):

    @swagger_auto_schema(
        tags=['Enrolment'], operation_description="To Enroll Course",
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


class CourseTrackingListView(UserAuthAPIView):

    @swagger_auto_schema(tags=['Enrolment'], operation_description="Get Tracking Materi", responses={
        200: CourseTrackingListSerializer()
    })
    def get(self, request, id):
        course = get_object_or_404(Courses, id=id)
        serializer = CourseTrackingListSerializer(course, user=request.user)
        return Response(serializer.data)


class FinishCourseView(UserAuthAPIView):
    @swagger_auto_schema(tags=['Enrolment'], operation_description="Finish Course", responses={
        200: MessageSuccesSerializer(),
        400: ErrorMessageSerializer()
    })
    def get(self, request, id):
        course = get_object_or_404(Courses, id=id)
        enroll = Enrollment.objects.filter(course=course, user=request.user).first()

        if not enroll:
            return ErrorResponse(error_message=_(f'Kamu belum mendaftar di {course.title}'))

        # cek ketika belom menyelesaikan semua module dan bab.
        if course.progress_percentage(request.user, on_thousand=True) != 100:
            return ErrorResponse(error_message=_(f'Kamu belom menyelesaikan semua materi {course.title}'))

        enroll.status = Enrollment.STATUS.finish
        if not enroll.finishing_date:
            enroll.finishing_date = timezone.now().date()
            utils.send_notification(request.user, f'Selamat!',
                                    f'Selamat!, anda berhasil menyelesaikan kelas {enroll.course.title}')

        return Response({'message': _(f'Kamu berhasil menyelesaikan kelas {enroll.course.title}')})
