from django.urls import path, include
from . import views

app_name = 'sections'
urlpatterns = [
    path('<int:id>', views.index, name='index'),
    path('<int:id>/add/', views.create, name='add'),
    path('<int:id>/edit/', views.edit, name='edit'),
    path('<int:id>/delete/', views.delete, name='delete'),
    path('details/<int:id>', views.details, name='details'),
    path('<int:id>/task-setting/', views.task_setting, name='task_setting'),

]
