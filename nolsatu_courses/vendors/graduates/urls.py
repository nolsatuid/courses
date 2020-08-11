from django.urls import path
from . import views

app_name = 'graduates'
urlpatterns = [
    path('candidate/', views.candidate, name='candidate'),
    path('candidate-to-graduate/<int:candidate_id>', views.candidate_to_graduate, name='candidate_to_graduate'),
    path('', views.graduate, name='index'),

]
