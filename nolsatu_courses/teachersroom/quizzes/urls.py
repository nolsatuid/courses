from django.urls import path, include
from . import views

app_name = 'quizzes'
urlpatterns = [
    path('', views.results, name='results'),
    path('detail-result/<int:id>/<int:batch>', views.detail_result, name='detail_result'),
]
