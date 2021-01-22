from django.urls import path, include
from . import views

app_name = 'quizzes'
urlpatterns = [
    path('', views.results, name='results'),
]
