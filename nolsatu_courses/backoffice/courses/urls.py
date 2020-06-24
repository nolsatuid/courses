from django.urls import path, include
from . import views

app_name = 'courses'
urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add, name='add'),
    path('<int:id>/edit/', views.edit, name='edit'),
    path('<int:id>/delete/', views.delete, name='delete'),
    path('details/<int:id>', views.details, name='details'),
    path('registrants/', views.registrants, name='registrants'),
    path('ajax-change-status-registrants/',
         views.ajax_change_status_registrants, name='ajax_change_status_registrants'),
    path('bulk-register/', views.bulk_register, name='bulk_register'),
    path('<int:id>/export/', views.export_data, name='export_data'),
]
