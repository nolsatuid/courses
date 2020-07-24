from django.urls import path, include
from . import views

app_name = 'batchs'
urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.create, name='add'),
    path('details/<int:id>', views.details, name='details'),
    path('<int:id>/edit/', views.edit, name='edit'),
    path('<int:id>/delete/', views.delete, name='delete'),
]
