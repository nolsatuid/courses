from django.urls import path, include
from . import views

app_name = 'courses'
urlpatterns = [
    path('<int:id>', views.details, name='details'),
]
