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
    path('category', views.list_category, name='category'),
    path('add-category/', views.create_category, name='add_category'),
    path('edit-category/<int:category_id>', views.edit_category, name='edit_category'),
    path('delete-category/<int:category_id>', views.delete_category, name='delete_category'),
    path('<int:category_id>/sub-category', views.list_sub_category, name='sub_category'),
    path('<int:category_id>/add-sub-category', views.create_sub_category, name='add_sub_category'),
    path('delete-sub_category/<int:sub_category_id>', views.delete_sub_category, name='delete_sub_category'),
    path('edit-sub-category/<int:sub_category_id>', views.edit_sub_category, name='edit_sub_category'),

]
