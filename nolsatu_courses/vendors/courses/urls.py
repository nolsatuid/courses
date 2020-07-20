from django.urls import path, include
from . import views

app_name = 'courses'
urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.create, name='add'),
    path('details/<int:courses_id>', views.details, name='details'),
]
