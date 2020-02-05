from django.urls import path, include

app_name = "api"
urlpatterns = [
    path('demo', include('nolsatu_courses.api.demo.urls')),
]
