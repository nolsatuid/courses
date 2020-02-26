from django.urls import path
from . import views

app_name = "courses"
urlpatterns = [
    path('list', views.CourseListView.as_view(), name='list'),
    path('detail/<int:id>', views.CourseDetailView.as_view(), name='detail'),
    path('detail/<int:id>/enroll/', views.CourseEnrollDetailView.as_view(), name='detail_enroll'),
    path('<int:id>/enroll/', views.EnrollCourseView.as_view(), name='enroll'),
    path('preview/list/<int:id>', views.CoursePreviewListView.as_view(), name='preview_list'),
    path('module/preview/<int:id>', views.ModulePreviewView.as_view(), name='module_preview'),
    path('section/preview/<int:id>', views.SectionPreviewView.as_view(), name='section_preview'),
    path('module/detail/<int:id>', views.ModuleDetailView.as_view(), name='module_detail'),
]
