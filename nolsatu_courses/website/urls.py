from django.urls import path, include
from . import views

app_name = 'website'
urlpatterns = [
    path('', views.index, name='index'),
    path('tes_login/', views.test_login, name='test_login'),
    path('logout', views.logout, name='logout'),
    path('login', views.login, name='login'),
    path('courses/', include('nolsatu_courses.website.courses.urls')),
    path('modules/', include('nolsatu_courses.website.modules.urls')),
    path('sections/', include('nolsatu_courses.website.sections.urls')),
]
