from django.urls import path, include
from . import views

app_name = 'graduates'
urlpatterns = [
    path('', views.index, name='index'),
    path('candidate/', views.candidate, name='candidate'),
    path('ajax-filter-batch/', views.ajax_filter_batch, name='ajax_filter_batch'),
    path('candidate-to-graduate/<int:id>', views.candidate_to_graduate, name='candidate_to_graduate'),
    path('regenerate-certificate/<int:user_id>', views.regenerate_certificate, name='regenerate_certificate'),
]
