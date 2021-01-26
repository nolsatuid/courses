from django.urls import path, include
from . import views

app_name = 'teachersroom'
urlpatterns = [
    path('', views.index, name='index'),
    path('courses/', include('nolsatu_courses.teachersroom.courses.urls')),
    path('quizzes/', include('nolsatu_courses.teachersroom.quizzes.urls')),
    path('graduates/', include('nolsatu_courses.teachersroom.graduates.urls')),
    path('task/', include('nolsatu_courses.teachersroom.tasks.urls')),

]
