from django.urls import path, include
from . import views

app_name = 'quizzes'
urlpatterns = [
    path('', views.index, name='index'),
    path('detail-result/<int:id>', views.detail_result, name='detail_result'),
    path('participant-result/<int:id>', views.participant_result, name='participant_result'),
]
