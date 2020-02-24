from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.api.response import ErrorResponse
from nolsatu_courses.api.modules.serializers import ModuleDetailSerializer
from nolsatu_courses.api.authentications import UserAuthAPIView
from nolsatu_courses.apps.courses.models import Module
from nolsatu_courses.website.modules.views import get_pagination


class ModuleDetailView(UserAuthAPIView):

    @swagger_auto_schema(tags=['Modules from course'], operation_description="Get Module Detail", responses={
        200: ModuleDetailSerializer()
    })
    def get(self, request, slug):
        module = get_object_or_404(Module, slug=slug)
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
