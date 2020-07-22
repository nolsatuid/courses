from django.urls import path, include
from . import views

app_name = 'sections'
urlpatterns = [
    path('<int:id>', views.index, name='index'),
]
