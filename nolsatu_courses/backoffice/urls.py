from django.urls import path, include
from . import views

app_name = 'backoffice'
urlpatterns = [
    path('', views.index, name='index'),
    path('courses/', include('nolsatu_courses.backoffice.courses.urls')),
    path('modules/', include('nolsatu_courses.backoffice.modules.urls')),
    path('sections/', include('nolsatu_courses.backoffice.sections.urls')),
    path('tasks/', include('nolsatu_courses.backoffice.tasks.urls')),
]
