from django.urls import path, include
from . import views

app_name = 'tasks'
urlpatterns = [
    path('', views.index, name='index'),
    path('ajax-filter-section/', views.ajax_filter_section, name='ajax_filter_section'),
    path('ajax-filter-batch/', views.ajax_filter_batch, name='ajax_filter_batch'),
    path('ajax-change-status/', views.ajax_change_status, name='ajax_change_status'),
]
