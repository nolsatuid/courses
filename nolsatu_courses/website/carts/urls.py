from django.urls import path
from . import views

app_name = 'carts'
urlpatterns = [
    path('', views.cart, name='index'),
    path('<str:cart_id>/delete/', views.cart_delete, name='cart_delete'),
    path('<str:product_id>/add/', views.add_item, name='add_item'),
    path('choose-item/', views.choose_item, name='choose_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/', views.payment, name='payment'),
]