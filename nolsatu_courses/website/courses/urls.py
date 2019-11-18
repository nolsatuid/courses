from django.urls import path, include
from . import views

app_name = 'courses'
urlpatterns = [
    path('', views.user_courses, name='user_courses'),
    path('<slug:slug>', views.details, name='details'),
]
