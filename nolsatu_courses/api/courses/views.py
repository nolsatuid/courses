from django.conf import settings
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from nolsatu_courses.api.authentications import UserAuthAPIView, InternalAPIView, InternalAPIMixin, UserAuthMixin
from nolsatu_courses.api.courses.serializers import (
    SimpleCourseSerializer, CourseDetailBatchSerializer, CourseEnrollSerializer, CoursePreviewListSerializer,
    ModulePreviewSerializer, SectionPreviewSerializer, ModuleDetailSerializer, SectionDetailSerializer,
    CollectTaskSerializer, CourseTrackingListSerializer, UserReportTaskSerializer, MyQuizSerializer,
    SimpleCourseProgress, CoursesIdSerializer,
)
from nolsatu_courses.api.response import ErrorResponse
from nolsatu_courses.api.serializers import MessageSuccesSerializer, ErrorMessageSerializer
from nolsatu_courses.apps import utils
from nolsatu_courses.apps.courses.models import Courses, Module, Section, Enrollment, CollectTask
from nolsatu_courses.website.modules.views import get_pagination as get_pagination_module
from nolsatu_courses.website.sections.views import get_pagination as get_pagination_section
from quiz.models import Sitting


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Courses'], operation_description="Get Course List"
))
class CourseListView(InternalAPIMixin, ListAPIView):
    serializer_class = SimpleCourseSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_superuser:
            courses = Courses.objects.all()
        else:
            courses = Courses.objects.filter(is_visible=True, status=Courses.STATUS.publish)

        if self.request.query_params.get('search'):
            courses = courses.filter(title__icontains=self.request.query_params.get('search'))

        return courses


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Courses'], operation_description="Get My Course"
))
class MyCourseView(UserAuthMixin, ListAPIView):
    serializer_class = SimpleCourseProgress

    def get_queryset(self):
        return Courses.objects.filter(enrolled__user=self.request.user).all()


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Courses'], operation_description="Get Course Detail"
))
class CourseDetailView(InternalAPIMixin, RetrieveAPIView):
    serializer_class = CourseDetailBatchSerializer
    lookup_field = 'id'
    queryset = Courses.objects

    def get_object(self):
        obj = super().get_object()
        return {
            "course": obj,
            "batch": obj.get_last_batch(),
            'can_register': obj.can_register(self.request.user),
            'has_enrolled': obj.has_enrolled(self.request.user),
            'enroll': obj.get_enroll(self.request.user)
        }


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Courses'], operation_description="Get Course Preview List"
))
class CoursePreviewListView(InternalAPIMixin, RetrieveAPIView):
    serializer_class = CoursePreviewListSerializer
    lookup_field = 'id'
    queryset = Courses.objects


@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Courses'], operation_description="Get Course ID by Slug"
))
class CourseIdView(InternalAPIMixin, RetrieveAPIView):
    serializer_class = CoursesIdSerializer
    lookup_field = 'slug'
    queryset = Courses.objects



# TODO: Refactor, move to separate package

class MyTaskListView(UserAuthMixin, APIView):
    @swagger_auto_schema(tags=['Task'], operation_description="Get My Grade", responses={
        200: UserReportTaskSerializer(many=True)
    })
    def get(self, request, course_id):
        my_tasks = CollectTask.objects.filter(
            section__module__course=course_id, user=request.user
        ).values_list('section__title', 'score', 'note', 'create_at', 'update_at')
        data = [{'section_name': x[0], 'score': x[1], 'note': x[2], 'create_at': x[3],
                 'update_at': x[4]} for x in my_tasks]
        serializer = UserReportTaskSerializer(data, many=True)
        return Response(serializer.data)

class ModulePreviewView(InternalAPIView):
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
        pagination = get_pagination_module(request, module, set_session=True)

        # handle ketika user belum mengumpulkan tugas pada sesi sebelumnya
        # jika page_type adalah section dan section memiliki tugas
        if pagination['prev_type'] == 'section' and pagination['prev'].is_task:
            if not pagination['prev'].collect_task.all():
                return ErrorResponse(
                    error_message=_(f"Kamu harus mengumpulkan tugas pada sesi {pagination['prev'].title}"))

        # save activities user to module
        if module.has_enrolled(request.user):
            module.get_or_create_activity(user=request.user, course=module.course)
            module.delete_cache(request.user)

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


class SectionPreviewView(InternalAPIView):

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

        # dapatkan pagination
        pagination = get_pagination_section(request, section)
        prev_type = pagination['prev_type']
        prev = pagination['prev']

        # handle ketika user belum mengumpulkan tugas pada sesi sebelumnya
        # jika page_type adalah section dan section memiliki tugas
        if prev_type == 'section' and prev.is_task:
            if not request.user.collect_tasks.filter(section=prev):
                return ErrorResponse(
                    error_message=_(f"Kamu harus mengumpulkan tugas pada sesi {prev.title}"))

        # save activities user to module
        if section.has_enrolled(request.user):
            section.get_or_create_activity(user=request.user,
                                           course=section.module.course)
            section.delete_cache(request.user)

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

        if course.product and course.product.price > 0:
            return ErrorResponse(error_message=_(f'Kamu harus melakukan pembelian kursus'
                                                 f' {course.title} terlebih dahulu !'))

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

        if enroll.status != Enrollment.STATUS.graduate and enroll.status != Enrollment.STATUS.finish:
            
            enroll.status = Enrollment.STATUS.finish
            enroll.finishing_date = timezone.now().date()
            enroll.save()

            utils.send_notification(request.user, f'Selamat!',
                                    f'Selamat!, anda berhasil menyelesaikan kelas {enroll.course.title}')

            return Response({'message': _(f'Kamu berhasil menyelesaikan kelas {enroll.course.title}')})
        else:
            return Response({'message': _(f'Kamu Telah Lulus dari kelas {enroll.course.title}')})


class MyQuizListView(UserAuthAPIView):
    @swagger_auto_schema(tags=['Quiz'], operation_description="Get My Quiz", responses={
        200: MyQuizSerializer(many=True)
    })
    def get(self, request, course_id):
        sitting = Sitting.objects.filter(user=request.user, quiz__courses__id=course_id)
        data = [{
            'name': sit.quiz,
            'score': sit.get_percent_correct
        } for sit in sitting]
        serializer = MyQuizSerializer(data, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
