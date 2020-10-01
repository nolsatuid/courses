from django.urls import path
from . import views

app_name = "carts"
urlpatterns = [
    path('add-item', views.AddToCartView.as_view(), name='add_item'),
]
