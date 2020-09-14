from django.urls import path
from . import views

app_name = 'carts'
urlpatterns = [
    path('', views.cart, name='index'),
    path('<str:cart_id>/delete', views.cart_delete, name='cart_delete'),
]