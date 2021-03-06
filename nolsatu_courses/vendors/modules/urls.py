from django.urls import path, include
from . import views

app_name = 'modules'
urlpatterns = [
    path('<int:id>', views.index, name='index'),
    path('<int:id>/add/', views.create, name='add'),
    path('details/<int:id>', views.details, name='details'),
    path('<int:id>/edit/', views.edit, name='edit'),
    path('<int:id>/delete/', views.delete, name='delete'),
    path('preview/<int:id>', views.preview, name='preview'),
]
