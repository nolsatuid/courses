from django.urls import path
from . import views

app_name = 'products'
urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add, name='add'),
    path('<int:product_id>/edit/', views.edit, name='edit'),
    path('<int:product_id>/delete/', views.delete, name='delete'),

]
