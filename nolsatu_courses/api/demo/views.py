from django.conf import settings
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from nolsatu_courses.api.authentications import UserAPIServiceAuthentication
from nolsatu_courses.apps.utils import call_internal_api


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([UserAPIServiceAuthentication])
@permission_classes([IsAuthenticated])
def demo_view(request):
    # Calling internal API
    response_get = call_internal_api('get', url=settings.NOLSATU_HOST + '/api/internal/demo').json()

    request_data = {
        'user_id': 120,
        'other_info': 'Hellow'
    }

    response_post = call_internal_api(
        'post',
        url=settings.NOLSATU_HOST + '/api/internal/demo',
        data=request_data
    ).json()

    return Response(data={
        'message': 'Success Gan ',
        'internal_response_get': response_get,
        'internal_response_post': response_post,
        'is_authenticated':  str(request.user.is_authenticated),
        'user_name': getattr(request.user, 'first_name', 'No Name')
    })
