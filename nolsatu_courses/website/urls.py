from django.urls import path, include
from django.conf.urls import handler404, handler500
from . import views

app_name = 'website'
urlpatterns = [
    path('', views.index, name='index'),
    path('search', views.search, name='search'),
    path('tes_login/', views.test_login, name='test_login'),
    path('logout', views.logout, name='logout'),
    path('login', views.login, name='login'),
    path('courses/', include('nolsatu_courses.website.courses.urls')),
    path('modules/', include('nolsatu_courses.website.modules.urls')),
    path('sections/', include('nolsatu_courses.website.sections.urls')),
    path('apps/', include('nolsatu_courses.website.apps.urls')),
    path('error404/', views.error_404, name='error404'),
    path('error500/', views.error_500, name='error500'),
]