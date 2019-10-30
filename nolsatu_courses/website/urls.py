from django.urls import path, include
from . import views

app_name = 'website'
urlpatterns = [
    path('', views.index, name='index'),
    path('courses/', include('nolsatu_courses.website.courses.urls')),
]
