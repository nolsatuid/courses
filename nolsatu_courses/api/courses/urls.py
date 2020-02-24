from django.urls import path
from . import views

app_name = "courses"
urlpatterns = [
    path('list', views.CourseListView.as_view(), name='list'),
    path('detail/<int:id>', views.CourseDetailView.as_view(), name='detail'),
    path('detail/enroll/<int:id>', views.CourseEnrollDetailView.as_view(), name='detail_enroll'),
]
