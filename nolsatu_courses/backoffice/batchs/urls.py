from django.urls import path
from . import views

app_name = 'batchs'
urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add, name='add'),
    path('<int:id>/edit/', views.edit, name='edit'),
    path('<int:id>/delete/', views.delete, name='delete'),
    path('details/<int:id>', views.details, name='details'),
    path('assign_instructor/<int:id>', views.assign_instructor, name='assign_instructor')
]
