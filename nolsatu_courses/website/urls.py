from django.urls import path, include
from . import views

app_name = 'website'
urlpatterns = [
    path('', views.index, name='index'),
]
