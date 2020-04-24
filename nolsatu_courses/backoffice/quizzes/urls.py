from django.urls import path, include
from . import views

app_name = 'quizzes'
urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add, name='add'),
    path('<int:id>/edit/', views.edit, name='edit'),
    path('results', views.results, name='results'),
    path('detail-result/<int:id>', views.detail_result, name='detail_result'),
    path('participant-result/<int:id>', views.participant_result, name='participant_result'),
    path('list/<int:id>', views.participant_result, name='participant_result'),
]
