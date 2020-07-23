from django.urls import path, include
from . import views

app_name = 'batchs'
urlpatterns = [
    path('', views.index, name='index'),

]
