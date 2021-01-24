from django.urls import path, include
from . import views

app_name = 'graduates'
urlpatterns = [
    path('candidate/', views.candidate, name='candidate'),
]
