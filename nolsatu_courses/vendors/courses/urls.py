from django.urls import path, include
from . import views

app_name = 'courses'
urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.create, name='add'),
    path('details/<int:courses_id>', views.details, name='details'),
    path('<int:id>/delete/', views.delete, name='delete'),
    path('<int:id>/edit/', views.edit, name='edit'),
    path('registrants/', views.registrants, name='registrants'),
    path('ajax-change-status-registrants/',
         views.ajax_change_status_registrants, name='ajax_change_status_registrants'),
]
