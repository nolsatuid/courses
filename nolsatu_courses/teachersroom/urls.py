from django.urls import path, include
from . import views

app_name = 'teachersroom'
urlpatterns = [
    path('', views.index, name='index'),
    path("courses/", include('nolsatu_courses.teachersroom.courses.urls'))
]
