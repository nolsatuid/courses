from django.urls import path, include
from . import views

app_name = 'graduates'
urlpatterns = [
    path('', views.index, name='index'),
    path('candidate/', views.candidate, name='candidate'),
]
