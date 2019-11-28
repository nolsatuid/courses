from django.urls import path, include
from . import views

app_name = 'sections'
urlpatterns = [
    path('<slug:slug>', views.details, name='details'),
    path('preview/<slug:slug>', views.preview, name='preview'),
]
