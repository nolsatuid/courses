from django.urls import path, include
from . import views

app_name = 'backoffice'
urlpatterns = [
    path('', views.index, name='index'),
    path('courses/', include('nolsatu_courses.backoffice.courses.urls'))
]
