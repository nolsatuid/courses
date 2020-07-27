from django.urls import path, include
from . import views

app_name = 'tasks'
urlpatterns = [
    path('', views.index, name='index'),
    path('ajax-change-status/', views.ajax_change_status, name='ajax_change_status'),
    path('report/', views.report_index, name='report_index'),
]
