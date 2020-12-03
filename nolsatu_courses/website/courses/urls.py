from django.urls import path, include, re_path
from . import views

app_name = 'courses'
urlpatterns = [
    path('', views.user_courses, name='user_courses'),
    path('<slug:slug>', views.details, name='details'),
    path('enroll/<slug:slug>', views.enroll, name='enroll'),
    path('finish/<slug:slug>', views.finish, name='finish'),
    path('quizzes/<int:course_id>/', views.user_quizzes, name='user_quizzes'),
    path('tasks/<int:course_id>/', views.user_tasks, name='user_tasks'),
]
