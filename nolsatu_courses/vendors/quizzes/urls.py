from django.urls import path, include
from . import views

app_name = 'quizzes'
urlpatterns = [
    path('category', views.list_category, name='category'),
    path('add-category/', views.create_category, name='add_category'),
    path('edit-category/<int:category_id>', views.edit_category, name='edit_category'),
    path('delete-category/<int:category_id>', views.delete_category, name='delete_category'),
]
