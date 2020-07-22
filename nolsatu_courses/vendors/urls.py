from django.urls import path, include
from . import views

app_name = 'vendors'
urlpatterns = [
    path('', views.index, name='index'),
    path('courses/', include('nolsatu_courses.vendors.courses.urls')),
    path('modules/', include('nolsatu_courses.vendors.modules.urls')),
]
