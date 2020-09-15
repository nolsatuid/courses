from django.urls import path, include
from . import views

app_name = 'orders'
urlpatterns = [
    path('', views.index, name='index'),
    path('details/<int:id>', views.details, name='details')
]
