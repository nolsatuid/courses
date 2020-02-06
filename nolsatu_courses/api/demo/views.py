from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from nolsatu_courses.api.authentications import UserAPIServiceAuthentication


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([UserAPIServiceAuthentication])
@permission_classes([IsAuthenticated])
def demo_view(request):
    return Response(data={
        'message': 'Success Gan ',
        'is_authenticated':  str(request.user.is_authenticated),
        'user_name': getattr(request.user, 'first_name', 'No Name')
    })
