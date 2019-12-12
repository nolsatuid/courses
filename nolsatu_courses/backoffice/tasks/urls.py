from django.urls import path, include
from . import views

app_name = 'tasks'
urlpatterns = [
    path('index/', views.index, name='index'),
    path('ajax-filter-section/', views.ajax_filter_section, name='ajax_filter_section'),
    path('ajax-change-status/', views.ajax_change_status, name='ajax_change_status'),
]
