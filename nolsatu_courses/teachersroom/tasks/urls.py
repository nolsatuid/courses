from django.urls import path, include
from . import views

app_name = 'tasks'
urlpatterns = [
    path('', views.index, name='index'),
    path('report/', views.report_index, name='report_index'),
    path('report/<int:user_id>/<int:course_id>/<int:batch_id>', views.report_detail, name='report_detail'),
]
