from django.urls import path, include
from . import views

app_name = 'courses'
urlpatterns = [
    path('', views.get_list_courses, name='index'),
    path('add/', views.create_course, name='add'),
    path('details/<int:courses_id>', views.get_details_courses, name='details'),
]
