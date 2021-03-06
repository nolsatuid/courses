from django.urls import path, include
from . import views

app_name = 'quizzes'
urlpatterns = [
    path('category', views.list_category, name='category'),
    path('add-category/', views.create_category, name='add_category'),
    path('edit-category/<int:category_id>', views.edit_category, name='edit_category'),
    path('delete-category/<int:category_id>', views.delete_category, name='delete_category'),
    path('<int:category_id>/sub-category', views.list_sub_category, name='sub_category'),
    path('<int:category_id>/add-sub-category', views.create_sub_category, name='add_sub_category'),
    path('delete-sub_category/<int:sub_category_id>', views.delete_sub_category, name='delete_sub_category'),
    path('edit-sub-category/<int:sub_category_id>', views.edit_sub_category, name='edit_sub_category'),
    path('ajax-filter-sub-category/', views.ajax_filter_subcategory, name='ajax_filter_subcategory'),
    path('question/', views.list_question, name='question'),
    path('add-question/', views.create_question, name='create_question'),
    path('edit-question/<int:question_id>', views.edit_question, name='edit_question'),
    path('delete-question/<int:question_id>', views.delete_question, name='delete_question'),
    path('quiz/', views.list_quiz, name='list_quiz'),
    path('add-quiz/', views.create_quiz, name='create_quiz'),
    path('edit-quiz/<int:quiz_id>', views.edit_quiz, name='edit_quiz'),
    path('result', views.result_quiz, name='result_quiz'),
    path('detail-result/<int:quiz_id>/<int:batch_id>', views.detail_result, name='detail_result'),
    path('participant-result/<int:id>/<int:batch>', views.participant_result, name='participant_result'),
]
