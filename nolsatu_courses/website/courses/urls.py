from django.urls import path, include
from . import views

app_name = 'courses'
urlpatterns = [
    path('<slug:slug>', views.details, name='details'),
]
