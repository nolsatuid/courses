from django.urls import path, include
from . import views

app_name = 'quizzes'
urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add, name='add'),
    path('<int:id>/edit/', views.edit, name='edit'),
    path('results', views.results, name='results'),
    path('detail-result/<int:id>/<int:batch>', views.detail_result, name='detail_result'),
    path('participant-result/<int:id>/<int:batch>', views.participant_result, name='participant_result'),
    path('ajax-filter-sub-category/', views.ajax_filter_sub_category, name='ajax_filter_sub_category'),
    path('ajax-filter-questions/', views.ajax_filter_questions, name='ajax_filter_questions'),
]
