from django.urls import path, include
from . import views

app_name = 'vendors'
urlpatterns = [
    path('', views.index, name='index'),
    path('courses/', include('nolsatu_courses.vendors.courses.urls')),
    path('modules/', include('nolsatu_courses.vendors.modules.urls')),
    path('sections/', include('nolsatu_courses.vendors.sections.urls')),
    path('batchs/', include('nolsatu_courses.vendors.batchs.urls')),
    path('tasks/', include('nolsatu_courses.vendors.tasks.urls')),
    path('quizzes/', include('nolsatu_courses.vendors.quizzes.urls')),
    path('graduates/', include('nolsatu_courses.vendors.graduates.urls')),
    path('orders/', include('nolsatu_courses.vendors.orders.urls')),
]
