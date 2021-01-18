from django.urls import path
from . import views

app_name = 'orders'
urlpatterns = [
    path('', views.index, name='index'),
    path('details/<int:order_id>', views.details, name='details'),
    path('cancel/<int:order_id>', views.cancel, name='cancel')
]
