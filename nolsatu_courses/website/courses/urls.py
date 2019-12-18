from django.urls import path, include
from . import views

app_name = 'courses'
urlpatterns = [
    path('', views.user_courses, name='user_courses'),
    path('<slug:slug>', views.details, name='details'),
    path('enroll/<slug:slug>', views.enroll, name='enroll'),
    path('finish/<slug:slug>', views.finish, name='finish'),
]
