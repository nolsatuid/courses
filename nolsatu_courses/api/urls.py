from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from nolsatu_courses.api.authentications import BasicApiDocAuthentication

app_name = "api"

schema_view = get_schema_view(
    openapi.Info(
        title="Courses API",
        default_version='v1',
        description="NolSatu Course API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=False,
    permission_classes=(permissions.IsAuthenticated,),
    authentication_classes=(BasicApiDocAuthentication,)
)

urlpatterns = [
    path('docs', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('demo', include('nolsatu_courses.api.demo.urls')),
    path('', include('nolsatu_courses.api.courses.urls')),
]
