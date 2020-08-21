from django.urls import path
from . import views

app_name = 'vendors'
urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add, name='add'),
    path('<int:vendor_id>/edit/', views.edit, name='edit'),
    path('<int:vendor_id>/delete/', views.delete, name='delete'),

]
