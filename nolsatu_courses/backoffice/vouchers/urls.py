from django.urls import path, include
from . import views

app_name = 'vouchers'
urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<int:id>', views.detail, name='detail'),
]
